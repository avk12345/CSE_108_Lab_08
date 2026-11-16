#!/usr/bin/env python3
"""Render the current Helix buffer with Glow, within the focused editor view."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import uuid

VERSION = '3.0.0'
ARCHIVES = {
    'x86_64': ('x86_64', '13e05e4b2acc18d2aee44291aefe6325b077ec321b631a0cfa780e8e3bc33f78'),
    'aarch64': ('arm64', '810c39f4691feb75e675a5f5f54b9fa091354e7599d9cf9c9fc9b97e47a99759'),
}
DATA = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'pond-devtools/glow'


def install(destination=None):
    arch, expected = ARCHIVES[platform.machine()]
    destination = Path(destination) if destination else DATA / VERSION / 'glow'
    if destination.exists():
        raise RuntimeError(f'Already exists; review before replacing: {destination}')
    url = f'https://github.com/charmbracelet/glow/releases/download/v{VERSION}/glow_{VERSION}_Linux_{arch}.tar.gz'
    with tempfile.TemporaryDirectory(prefix='pond-glow-install-') as directory:
        archive = Path(directory) / 'glow.tar.gz'
        urllib.request.urlretrieve(url, archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise RuntimeError('Glow release checksum mismatch')
        with tarfile.open(archive) as files:
            binary = next(m for m in files.getmembers() if m.isfile() and Path(m.name).name == 'glow')
            payload = files.extractfile(binary).read()
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + '.new')
        temporary.write_bytes(payload)
        temporary.chmod(0o755)
        temporary.replace(destination)
    print(f'Installed verified Glow {VERSION}: {destination}')


def session_directory():
    # Find the exact calling editor, including inside a PID namespace.
    pid = os.getppid()
    while pid > 1:
        proc = Path('/proc') / str(pid)
        stat = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
        if (proc / 'comm').read_text().strip() in ('helix', 'hx'):
            root = Path(os.environ.get('XDG_RUNTIME_DIR', tempfile.gettempdir())) / f'pond-glow-{os.getuid()}'
            root.mkdir(mode=0o700, exist_ok=True)
            if root.is_symlink() or root.stat().st_uid != os.getuid() or root.stat().st_mode & 0o077:
                raise RuntimeError('Unsafe preview directory')
            session = root / f'{pid}-{stat[19]}'
            session.mkdir(mode=0o700, exist_ok=True)
            return session
        pid = int(stat[1])
    raise RuntimeError('Preview must be called from Helix')


def capture(session):
    snapshot = session / 'pending.md'
    snapshot.write_bytes(sys.stdin.buffer.read())
    snapshot.chmod(0o600)


def toggle(session):
    # The quoted heredoc in the keymap transports names literally, including
    # quotes and shell metacharacters. Its // delimiter cannot occur in a
    # normalized Helix path. No filename or document text becomes shell code.
    name, line, column = sys.stdin.read().rstrip('\n').rsplit('\n', 2)
    path = Path(name).expanduser().absolute()
    if name == '[scratch]':
        raise RuntimeError('Save an unnamed buffer once before opening its preview')
    line, column = int(line), int(column)
    metadata = path.with_suffix('.json')
    if path.parent == session and path.suffix == '.pond-glow' and metadata.is_file():
        original = json.loads(metadata.read_text())
        print(f"{original['path']}:{original['line']}:{original['column']}")
        return
    glow = shutil.which('glow')
    if not glow:
        candidate = DATA / VERSION / 'glow'
        if candidate.is_file():
            glow = str(candidate)
    if not glow:
        raise RuntimeError('Glow is missing; install it before using the preview')
    result = subprocess.run(
        [glow, '--config', '/dev/null', '--style', 'notty', '--width', '80', '-'],
        input=(session / 'pending.md').read_bytes(), capture_output=True, check=True,
        env=dict(os.environ, NO_COLOR='1'), timeout=30,
    )
    # Helix buffers cannot interpret terminal escape sequences, including OSC 8
    # hyperlinks. Strip them, then use the normal Markdown highlighter.
    rendered = re.sub(rb'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)', b'', result.stdout)
    rendered = re.sub(rb'\x1b\[[0-?]*[ -/]*[@-~]', b'', rendered)
    rendered = b'\n'.join(row.rstrip() for row in rendered.splitlines()) + b'\n'
    preview = session / (uuid.uuid4().hex + '.pond-glow')
    preview.write_bytes(rendered)
    preview.chmod(0o400)
    preview.with_suffix('.json').write_text(json.dumps({'path': str(path), 'line': line, 'column': column}))
    print(preview)


def main():
    if sys.argv[1:2] == ['install']:
        install(sys.argv[2] if len(sys.argv) > 2 else None)
        return
    session = session_directory()
    if sys.argv[1:] == ['capture']:
        capture(session)
    elif sys.argv[1:] == ['toggle']:
        toggle(session)
    else:
        raise RuntimeError('Expected capture, toggle or install')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Glow preview: {error}', file=sys.stderr)
        sys.exit(1)
