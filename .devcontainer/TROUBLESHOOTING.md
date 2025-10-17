# DevContainer Troubleshooting Guide

## Common Issues and Solutions

### 1. Build Error: "Unable to locate package libta-lib0"

**Error Message:**
```
E: Unable to locate package libta-lib0
E: Unable to locate package libta-lib0-dev
```

**Status:** ✅ **FIXED**

**Solution:**
This has been fixed in the current Dockerfile. If you still see this error:

1. Make sure you have the latest `.devcontainer/Dockerfile`
2. In VS Code: Press `F1` → "Dev Containers: Rebuild Container"
3. Select "Rebuild Without Cache" if prompted

**Technical Details:**
- These packages don't exist in Debian's apt repositories
- TA-Lib is built from source instead (which is better anyway)
- The fix removes the unnecessary apt package lines

---

### 2. Build is Very Slow

**Symptoms:**
- First build takes 5-10+ minutes
- Downloading and compiling TA-Lib is slow

**Solutions:**

**This is Normal for First Build:**
- Subsequent builds use cache and take ~30 seconds
- The time is spent on:
  - Downloading base Python image (~1GB)
  - Installing system packages
  - Compiling TA-Lib from source (~2-3 minutes)
  - Installing Python packages

**To Speed Up:**
- Ensure good internet connection
- Don't interrupt the build process
- Future builds will be much faster (cached)

---

### 3. Container Won't Start

**Error:** "Cannot connect to Docker daemon"

**Solutions:**

1. **Check Docker is Running:**
   ```bash
   docker ps
   ```
   If error, start Docker Desktop

2. **Check Docker Resources:**
   - Open Docker Desktop → Settings → Resources
   - Minimum: 4GB RAM, 2 CPUs
   - Recommended: 8GB RAM, 4 CPUs

3. **Restart Docker:**
   ```bash
   sudo systemctl restart docker  # Linux
   # Or restart Docker Desktop on Windows/Mac
   ```

---

### 4. Port 8888 Already in Use

**Error:** "Port 8888 is already allocated"

**Solutions:**

**Option 1: Change Port in DevContainer**
Edit `.devcontainer/devcontainer.json`:
```json
"forwardPorts": [8889]  // Changed from 8888
```

**Option 2: Stop Conflicting Service**
```bash
# Find what's using port 8888
sudo lsof -i :8888
# Or on Windows:
netstat -ano | findstr :8888

# Stop Jupyter or other service using that port
```

---

### 5. Python Packages Not Found

**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Causes:**
- Post-create script failed
- Requirements not installed

**Solutions:**

1. **Check Post-Create Logs:**
   - Look in VS Code Output panel
   - Check for errors during `pip install`

2. **Manually Install:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Rebuild Container:**
   - F1 → "Dev Containers: Rebuild Container"

---

### 6. TA-Lib Import Error

**Error:** `ImportError: libta_lib.so.0: cannot open shared object file`

**Cause:**
- TA-Lib C library not installed
- TA-Lib Python wrapper not installed

**Solutions:**

1. **Verify TA-Lib C Library:**
   ```bash
   ls /usr/lib/libta_lib.*
   # Should see: libta_lib.a, libta_lib.la, libta_lib.so, etc.
   ```

2. **Reinstall TA-Lib Python Wrapper:**
   ```bash
   pip uninstall TA-Lib
   pip install TA-Lib
   ```

3. **Rebuild Container:**
   - F1 → "Dev Containers: Rebuild Container Without Cache"

---

### 7. Permission Denied Errors

**Error:** "Permission denied" when writing files

**Cause:**
- User UID mismatch
- Volume mount permissions

**Solutions:**

1. **Check User:**
   ```bash
   whoami  # Should be: vscode
   id      # Check UID is 1000
   ```

2. **Fix Ownership:**
   ```bash
   sudo chown -R vscode:vscode /workspace
   ```

3. **Check Mount Options:**
   - Ensure workspace is bind-mounted correctly
   - Check `.devcontainer/devcontainer.json` mounts configuration

---

### 8. Git Configuration Issues

**Error:** "Please tell me who you are"

**Solution:**
Configure Git inside the container:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

This is normal on first use and only needs to be done once.

---

### 9. VS Code Extensions Not Loading

**Symptoms:**
- Python extension missing
- IntelliSense not working
- Jupyter not available

**Solutions:**

1. **Wait for Extensions to Install:**
   - First launch installs extensions automatically
   - Check bottom-left corner for progress

2. **Manually Install:**
   - Press `Ctrl+Shift+X`
   - Search and install: "Python", "Jupyter"

3. **Check Extensions.json:**
   - Verify `.vscode/extensions.json` exists
   - Rebuild container if missing

---

### 10. Out of Disk Space

**Error:** "No space left on device"

**Solutions:**

1. **Check Docker Disk Usage:**
   ```bash
   docker system df
   ```

2. **Clean Up Docker:**
   ```bash
   # Remove unused images, containers, volumes
   docker system prune -a

   # This frees several GB typically
   ```

3. **Increase Docker Disk Allocation:**
   - Docker Desktop → Settings → Resources → Disk image size
   - Increase to at least 60GB

---

### 11. Network/DNS Issues

**Error:** "Could not resolve host" during build

**Solutions:**

1. **Check Internet Connection:**
   ```bash
   ping 8.8.8.8
   ```

2. **Configure Docker DNS:**
   Edit Docker daemon config (`/etc/docker/daemon.json`):
   ```json
   {
     "dns": ["8.8.8.8", "8.8.4.4"]
   }
   ```

3. **Restart Docker:**
   ```bash
   sudo systemctl restart docker
   ```

---

### 12. Jupyter Lab Won't Start

**Error:** "Jupyter Lab not found"

**Solutions:**

1. **Install Jupyter:**
   ```bash
   pip install jupyterlab
   ```

2. **Start with Correct Parameters:**
   ```bash
   jupyter lab --ip=0.0.0.0 --no-browser
   ```

3. **Access via Forwarded Port:**
   - Check VS Code "Ports" panel
   - Open http://localhost:8888

---

### 13. Build Cache Issues

**Symptom:** Old code or configs persist after changes

**Solution:**

**Rebuild Without Cache:**
- F1 → "Dev Containers: Rebuild Container Without Cache"

Or via CLI:
```bash
docker build --no-cache -f .devcontainer/Dockerfile -t londonbreakout .
```

---

### 14. Container Crashes/Exits Immediately

**Symptoms:**
- Container starts then stops
- Can't connect to container

**Solutions:**

1. **Check Container Logs:**
   ```bash
   docker logs <container-name>
   ```

2. **Check Resource Limits:**
   - Ensure Docker has enough RAM/CPU
   - Close other applications

3. **Verify Dockerfile:**
   - Check for syntax errors
   - Ensure CMD doesn't exit immediately

---

## Getting Help

### Check Logs

**VS Code Logs:**
1. Press `Ctrl+Shift+P`
2. Search: "Developer: Show Logs"
3. Select: "Remote-Containers"

**Docker Logs:**
```bash
# Container logs
docker logs <container-name>

# Build logs
docker build -f .devcontainer/Dockerfile . 2>&1 | tee build.log
```

### Diagnostic Commands

Run these inside the container:
```bash
# Check Python
python --version
which python

# Check packages
pip list | grep -i 'pandas\|numpy\|talib'

# Check TA-Lib
python -c "import talib; print(talib.__version__)"

# Check disk space
df -h

# Check memory
free -h

# Check processes
ps aux
```

### Clean Slate

If all else fails, start fresh:
```bash
# Remove all containers
docker rm -f $(docker ps -aq)

# Remove all images
docker rmi -f $(docker images -q)

# Remove all volumes
docker volume prune -f

# Rebuild from scratch
# In VS Code: F1 → "Dev Containers: Rebuild Container Without Cache"
```

---

## Verified Working Configuration

**System Requirements:**
- Docker Desktop 20.10+
- VS Code 1.80+
- Dev Containers extension 0.300+
- 4GB+ RAM available
- 10GB+ disk space
- Internet connection

**Tested On:**
- ✅ Ubuntu 22.04 LTS
- ✅ Windows 11 + WSL2
- ✅ macOS 13+

**Build Time:**
- First build: 5-10 minutes
- Subsequent builds: 30-60 seconds

**Known Working Versions:**
- Python: 3.11
- Debian: Bullseye
- TA-Lib: 0.4.0
- NumPy: 1.24+
- Pandas: 2.0+

---

## Report Issues

If you encounter issues not covered here:

1. Check the changelog: `.devcontainer/CHANGELOG.md`
2. Review the main README: `README.md`
3. Check VS Code DevContainer docs: https://code.visualstudio.com/docs/devcontainers
4. Open an issue with:
   - Error message (full output)
   - System information
   - Steps to reproduce
   - Docker logs
   - VS Code logs

---

**Last Updated:** October 17, 2025
**Status:** All known issues resolved ✅
