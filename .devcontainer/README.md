# DevContainer for London Breakout Strategy

This DevContainer provides a complete development environment for the London Breakout trading strategy with all dependencies pre-installed.

## Features

- **Python 3.11** with all required packages
- **TA-Lib** pre-compiled and ready to use
- **Jupyter Lab** for interactive development
- **VS Code extensions** for Python development
- **Git** and GitHub CLI
- **Automated setup** via post-create script

## Quick Start

### Using VS Code

1. **Install Prerequisites:**
   - [Visual Studio Code](https://code.visualstudio.com/)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Open in Container:**
   - Open the project folder in VS Code
   - Press `F1` and select "Dev Containers: Reopen in Container"
   - Wait for the container to build (first time only, ~5-10 minutes)

3. **Start Coding:**
   - Container automatically installs all dependencies
   - Runs validation tests
   - Ready to use!

### Using Docker Compose

```bash
# Build and start
docker-compose -f .devcontainer/docker-compose.yml up -d

# Enter the container
docker-compose -f .devcontainer/docker-compose.yml exec app bash

# Stop
docker-compose -f .devcontainer/docker-compose.yml down
```

### Using Docker Directly

```bash
# Build the image
docker build -f .devcontainer/Dockerfile -t londonbreakout:latest .

# Run the container
docker run -it --rm \
  -v $(pwd):/workspace \
  -p 8888:8888 \
  londonbreakout:latest
```

## What's Included

### Base System
- Debian Bullseye (stable)
- Python 3.11
- Git, curl, wget, vim
- Build tools (gcc, g++, make, cmake)

### Python Packages
- **Core:** numpy, pandas, matplotlib, seaborn
- **Trading:** TA-Lib, pandas-ta, backtrader
- **API:** OpenApiPy (cTrader)
- **Development:** black, flake8, pylint, mypy, pytest
- **Jupyter:** jupyterlab, ipykernel, ipywidgets

### VS Code Extensions
- Python
- Pylance
- Jupyter
- Black Formatter
- GitLens
- Docker
- YAML
- Markdown
- Auto Docstring
- IntelliCode

### Tools
- Jupyter Lab (port 8888)
- Git & GitHub CLI
- Command history persistence
- Pip cache optimization

## Directory Structure

```
.devcontainer/
├── devcontainer.json    # VS Code DevContainer config
├── Dockerfile           # Container image definition
├── docker-compose.yml   # Docker Compose config
├── post-create.sh       # Setup script (runs automatically)
└── README.md           # This file
```

## Post-Create Setup

The container automatically runs `post-create.sh` which:

1. ✅ Installs all Python dependencies from `requirements.txt`
2. ✅ Installs cTrader OpenAPI
3. ✅ Creates necessary directories (data, logs, results)
4. ✅ Copies `.env.example` to `.env`
5. ✅ Sets executable permissions on scripts
6. ✅ Runs validation tests

## Common Tasks

### Run Backtest
```bash
python run_backtest.py
```

### Start Jupyter Lab
```bash
jupyter lab --ip=0.0.0.0 --no-browser
```
Then open http://localhost:8888

### Run Tests
```bash
python test_setup.py
```

### Optimize Parameters
```bash
python optimize.py
```

### Install Additional Packages
```bash
pip install <package-name>

# Add to requirements.txt to persist
echo "<package-name>" >> requirements.txt
```

## Environment Variables

Configure your cTrader credentials in `.env`:

```bash
CTRADER_CLIENT_ID=your_client_id
CTRADER_CLIENT_SECRET=your_client_secret
CTRADER_ACCESS_TOKEN=your_access_token
CTRADER_ACCOUNT_ID=your_account_id
```

## Troubleshooting

### Container won't build
- Check Docker is running
- Ensure you have enough disk space (need ~2GB)
- Try: `docker system prune` to free space

### TA-Lib installation fails
The Dockerfile builds TA-Lib from source, which should work. If it fails:
- Check the build logs
- You can comment out TA-Lib in `requirements.txt`
- Use `pandas-ta` as an alternative

### Python packages not found
Rebuild the container:
```bash
# In VS Code: F1 -> "Dev Containers: Rebuild Container"

# Or with Docker:
docker-compose -f .devcontainer/docker-compose.yml build --no-cache
```

### Jupyter not accessible
- Check port 8888 is not in use
- Ensure port forwarding is working
- Try accessing via container IP

### Permission issues
The container runs as non-root user `vscode` (UID 1000). If you have permission issues:
```bash
# Fix ownership
sudo chown -R 1000:1000 /workspace
```

## Customization

### Add VS Code Extensions
Edit `.devcontainer/devcontainer.json`:
```json
"extensions": [
  "ms-python.python",
  "your.extension.id"
]
```

### Change Python Version
Edit `.devcontainer/Dockerfile`:
```dockerfile
FROM python:3.12-bullseye  # Change version here
```

### Add System Packages
Edit `.devcontainer/Dockerfile`:
```dockerfile
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    your-package-name
```

### Modify Post-Create Script
Edit `.devcontainer/post-create.sh` to add custom setup steps.

## Performance Tips

1. **Use volumes for persistence:**
   - Command history is persisted
   - Pip cache is persisted
   - Workspace is bind-mounted

2. **Rebuild only when needed:**
   - Rebuilding takes time
   - Use `pip install` for Python packages first
   - Only rebuild for system-level changes

3. **Cache optimization:**
   - Docker layer caching speeds up rebuilds
   - Don't change Dockerfile unless necessary

## Security Notes

- Container runs as non-root user by default
- Never commit `.env` with real credentials
- Use demo account credentials for testing
- Keep your access tokens secure

## Additional Resources

- [VS Code DevContainers Docs](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Documentation](https://docs.docker.com/)
- [Python DevContainer Features](https://github.com/devcontainers/features/tree/main/src/python)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review container logs: `docker logs <container-id>`
3. Rebuild with no cache: `docker-compose build --no-cache`
4. Check project README.md for strategy-specific help

---

**Happy Containerized Trading!** 🐳🚀
