# DevContainer Quick Start

Get up and running in 3 steps with zero manual configuration!

## Prerequisites

Install these once:

1. **Docker Desktop** - https://www.docker.com/products/docker-desktop
   - Windows/Mac: Download and install
   - Linux: `sudo apt-get install docker.io docker-compose`

2. **Visual Studio Code** - https://code.visualstudio.com/

3. **Dev Containers Extension**
   - Open VS Code
   - Press `Ctrl+P` (or `Cmd+P` on Mac)
   - Type: `ext install ms-vscode-remote.remote-containers`
   - Press Enter

## Quick Start

### Step 1: Open in Container

```bash
# Open VS Code in the project directory
code /path/to/londonbreakout
```

Or: File → Open Folder → Select `londonbreakout`

### Step 2: Reopen in Container

Press `F1` and type: **"Dev Containers: Reopen in Container"**

Or click the blue button in the bottom-left corner: `><`

### Step 3: Wait for Setup

First time only (~5-10 minutes):
- Docker builds the image
- Installs Python 3.11
- Compiles TA-Lib
- Installs all dependencies
- Runs validation tests

Subsequent times: ~30 seconds (uses cached image)

### Step 4: You're Ready!

Once complete, you'll see:
- ✓ All dependencies installed
- ✓ TA-Lib working
- ✓ cTrader API ready
- ✓ Jupyter Lab available
- ✓ All VS Code extensions loaded

## What You Get

### Pre-installed Software
- Python 3.11
- TA-Lib (compiled and ready)
- NumPy, Pandas, Matplotlib
- Jupyter Lab
- All project dependencies
- Git, vim, curl, wget

### VS Code Extensions
- Python + Pylance
- Jupyter
- Black Formatter
- GitLens
- Docker
- CSV Rainbow
- Markdown tools

### Development Tools
- Debugger configured
- Tasks pre-configured
- Linting & formatting
- Testing framework
- Jupyter integration

## First Commands to Try

Open the integrated terminal (`Ctrl+``) and run:

```bash
# Test installation
python test_setup.py

# Run a backtest
python run_backtest.py

# Start Jupyter Lab
jupyter lab --ip=0.0.0.0

# Check Python packages
pip list
```

## VS Code Features

### Run Configurations (F5)
- Run Backtest
- Run Optimization
- Test Setup
- Debug Current File

### Tasks (Ctrl+Shift+B)
- Run Backtest (default)
- Run Optimization
- Generate Sample Data
- Start Jupyter Lab
- Format Code
- Lint Code

### Debugging
Set breakpoints and press F5 to debug!

## Accessing Jupyter Lab

After running `jupyter lab --ip=0.0.0.0`:

1. Look for the URL in terminal output
2. Click the link or copy to browser
3. Or just go to: http://localhost:8888

The port is automatically forwarded.

## Directory Persistence

Your work is safe! The following persist:
- ✅ Workspace files (bind-mounted)
- ✅ Command history
- ✅ Pip cache
- ✅ Git config
- ✅ Generated data/results

## Common Tasks

### Install Additional Packages
```bash
pip install package-name

# To persist, add to requirements.txt
echo "package-name" >> requirements.txt
```

### Rebuild Container
If you change Dockerfile or need fresh start:
- Press F1
- "Dev Containers: Rebuild Container"

### Stop Container
Just close VS Code. Container stops automatically.

### Remove Container
```bash
docker rm londonbreakout-dev
docker rmi londonbreakout:latest  # Remove image too
```

## Advantages

✅ **Zero Configuration** - Everything just works  
✅ **Consistent Environment** - Same setup for everyone  
✅ **No System Pollution** - Isolated from your OS  
✅ **Easy Sharing** - Share exact development environment  
✅ **Fast Setup** - 3 steps vs 30+ manual steps  
✅ **TA-Lib Pre-compiled** - No build hassles  
✅ **All Tools Included** - Linting, formatting, testing  

## Troubleshooting

### Container won't start
- Ensure Docker Desktop is running
- Check Docker has enough resources (4GB+ RAM)
- Try: `docker system prune` to free space

### Build fails
- Check internet connection
- Check Docker logs
- Try rebuilding: F1 → "Rebuild Container Without Cache"

### Port 8888 in use
Change port in `.devcontainer/devcontainer.json`:
```json
"forwardPorts": [8889]  // Changed from 8888
```

### Slow performance
- Increase Docker Desktop resources
- Use Docker volumes instead of bind mounts (advanced)

## Alternative: Docker CLI

Don't want VS Code? Use Docker directly:

```bash
# Build
docker build -f .devcontainer/Dockerfile -t londonbreakout .

# Run
docker run -it --rm \
  -v $(pwd):/workspace \
  -p 8888:8888 \
  londonbreakout

# Or use docker-compose
docker-compose -f .devcontainer/docker-compose.yml up
```

## Next Steps

1. ✅ Container running
2. ✅ Run `python test_setup.py` to validate
3. ✅ Read QUICKSTART.md for trading strategy guide
4. ✅ Try `python run_backtest.py`
5. ✅ Customize parameters in `config.py`
6. ✅ Build your trading strategy!

## Learn More

- [DevContainer Documentation](.devcontainer/README.md)
- [Project Documentation](README.md)
- [Quick Start Guide](QUICKSTART.md)
- [VS Code DevContainers](https://code.visualstudio.com/docs/devcontainers/containers)

---

**You're all set! Happy containerized trading!** 🐳🚀
