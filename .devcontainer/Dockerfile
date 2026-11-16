FROM node:24-bookworm AS node
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && npm install -g --allow-scripts=bun bun@1.4.4 typescript typescript-language-server pyright oxlint@1.93.0 oxfmt@0.78.0 \
 && arch="$(dpkg --print-architecture)" \
 && case "$arch" in amd64) helix_arch=x86_64 ;; arm64) helix_arch=aarch64 ;; *) exit 1 ;; esac \
 && curl -fsSL "https://github.com/helix-editor/helix/releases/download/25.07.1/helix-25.07.1-${helix_arch}-linux.tar.xz" -o /tmp/helix.tar.xz \
 && mkdir -p /opt/helix \
 && tar -xJf /tmp/helix.tar.xz -C /opt/helix --strip-components=1 \
 && ln -s /opt/helix/hx /usr/local/bin/hx \
 && rm /tmp/helix.tar.xz
ENV HELIX_RUNTIME=/opt/helix/runtime
COPY helix/pond-project.toml /opt/helix/runtime/themes/pond-project.toml
COPY --chown=vscode:vscode helix/config.toml /home/vscode/.config/helix/config.toml

# Pinned Glow reader and focused-view Helix preview integration.
COPY helix/pond-glow-preview.py /usr/local/lib/pond-glow-preview.py
RUN python3 /usr/local/lib/pond-glow-preview.py install /usr/local/bin/glow
COPY --chown=vscode:vscode helix/pond-glow-preview.py helix/languages.toml /home/vscode/.config/helix/
COPY --chown=vscode:vscode helix/runtime /home/vscode/.config/helix/runtime
