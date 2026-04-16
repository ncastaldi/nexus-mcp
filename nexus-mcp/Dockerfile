# Use official Python image
FROM python:3.11-slim

# 1. Install System Deps & PowerShell
# Explicitly linking the keyring to the source list to satisfy Debian Trixie security
RUN apt-get update && apt-get install -y \
    curl gnupg apt-transport-https ca-certificates \
    && curl -fSsL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /usr/share/keyrings/microsoft-prod.gpg > /dev/null \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/microsoft.list \
    && apt-get update && apt-get install -y powershell \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a symlink so 'powershell' command works in Linux
RUN ln -s /usr/bin/pwsh /usr/bin/powershell

WORKDIR /app

# 2. Use pyproject.toml to install dependencies
COPY pyproject.toml .
# Create dummy src so pip doesn't complain during the install
RUN mkdir src && pip install . 

# 3. Copy the actual source code
COPY src/ ./src/
COPY lib/ ./lib/

# 4. Runtime Config
ENV PYTHONPATH="/app/src:/app"
ENV PYTHONUNBUFFERED=1
CMD ["python", "src/main.py"]