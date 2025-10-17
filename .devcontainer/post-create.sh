#!/bin/bash

# Post-create script for DevContainer
# This runs after the container is created

set -e

echo "=========================================="
echo "DevContainer Post-Create Setup"
echo "=========================================="
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Requirements installed"
else
    echo "⚠ requirements.txt not found"
fi

# Install cTrader OpenAPI (optional, may fail if repo is down)
echo ""
echo "📡 Installing cTrader OpenAPI..."
pip install git+https://github.com/spotware/OpenApiPy.git || {
    echo "⚠ cTrader OpenAPI installation failed (optional - only needed for live trading)"
}

# Install pandas-ta (optional, TA-Lib already installed)
echo ""
echo "📊 Installing pandas-ta..."
pip install 'pandas-ta @ git+https://github.com/twopirllc/pandas-ta.git' || {
    echo "⚠ pandas-ta installation failed (optional - TA-Lib already works)"
}

# Create necessary directories
echo ""
echo "📁 Creating project directories..."
mkdir -p data
mkdir -p logs
mkdir -p results
echo "✓ Directories created"

# Set up git if not already configured
echo ""
echo "🔧 Configuring git..."
if [ -z "$(git config --global user.name)" ]; then
    echo "⚠ Git user.name not set. Configure with:"
    echo "   git config --global user.name 'Your Name'"
fi
if [ -z "$(git config --global user.email)" ]; then
    echo "⚠ Git user.email not set. Configure with:"
    echo "   git config --global user.email 'your.email@example.com'"
fi

# Copy .env.example to .env if it doesn't exist
echo ""
echo "🔐 Setting up environment variables..."
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file from .env.example"
    echo "  Remember to add your cTrader credentials!"
else
    echo "⚠ .env file already exists or .env.example not found"
fi

# Set correct permissions
echo ""
echo "🔑 Setting permissions..."
chmod +x run_backtest.py 2>/dev/null || true
chmod +x optimize.py 2>/dev/null || true
chmod +x test_setup.py 2>/dev/null || true
chmod +x .devcontainer/post-create.sh 2>/dev/null || true
echo "✓ Permissions set"

# Run setup validation
echo ""
echo "🧪 Running setup validation..."
if [ -f "test_setup.py" ]; then
    python test_setup.py || {
        echo "⚠ Some tests failed - check output above"
    }
else
    echo "⚠ test_setup.py not found"
fi

# Print welcome message
echo ""
echo "=========================================="
echo "✓ DevContainer Setup Complete!"
echo "=========================================="
echo ""
echo "Quick Start:"
echo "  1. Test installation:  python test_setup.py"
echo "  2. Run backtest:       python run_backtest.py"
echo "  3. Optimize:           python optimize.py"
echo "  4. Start Jupyter:      jupyter lab --ip=0.0.0.0"
echo ""
echo "Documentation:"
echo "  • QUICKSTART.md - 5-minute guide"
echo "  • README.md - Full documentation"
echo "  • config.py - Strategy parameters"
echo ""
echo "Happy Trading! 🚀"
echo ""
