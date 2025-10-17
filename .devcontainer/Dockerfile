# Use official Python image as base
FROM python:3.11-bullseye

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    # Common utilities
    git \
    curl \
    wget \
    vim \
    nano \
    less \
    sudo \
    # Build tools for Python packages
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    # Plotting dependencies
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    # Additional tools
    htop \
    tree \
    zip \
    unzip \
    jq \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib from source (more reliable than apt)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set up Python environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Install Python development tools
RUN pip install \
    # Linting and formatting
    black \
    flake8 \
    pylint \
    mypy \
    autopep8 \
    # Testing
    pytest \
    pytest-cov \
    pytest-mock \
    # Documentation
    sphinx \
    # Jupyter
    jupyter \
    jupyterlab \
    ipykernel \
    ipywidgets \
    # Debugging
    ipdb \
    debugpy

# Create workspace directory
RUN mkdir -p /workspace && chown -R $USERNAME:$USERNAME /workspace

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

# Set the default user
USER $USERNAME

# Set working directory
WORKDIR /workspace

# Expose Jupyter port
EXPOSE 8888

# Default command
CMD ["/bin/bash"]
