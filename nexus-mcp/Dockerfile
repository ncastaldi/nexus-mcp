FROM python:3.11-slim

# 1. Install System Deps & PowerShell
RUN apt-get update && apt-get install -y \
    curl gnupg apt-transport-https \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/microsoft.list \
    && apt-get update && apt-get install -y powershell \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/pwsh /usr/bin/powershell

WORKDIR /app

# 2. Use pyproject.toml to install dependencies
# We copy the pyproject.toml first to cache the 'pip install' layer
COPY pyproject.toml .
# Create a dummy src dir so pip doesn't complain during the install
RUN mkdir src && pip install . 

# 3. Copy the actual source code
COPY src/ ./src/
COPY lib/ ./lib/

# 4. Runtime Config
ENV PYTHONPATH="/app/src:/app"
# This matches the [project.scripts] entry in your toml
CMD ["python", "src/main.py"]