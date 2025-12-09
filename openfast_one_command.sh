#!/usr/bin/env bash
# Single-command setup to build and run OpenFAST in Docker on macOS (Intel or Apple Silicon).
# Usage: bash openfast_one_command.sh [workdir]
# If workdir is omitted, a folder named openfast-docker will be created under the current directory.
set -euo pipefail

WORKDIR=${1:-"$PWD/openfast-docker"}
echo "Using work directory: $WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

# Clone OpenFAST only if it is not already present
if [ ! -d openfast ]; then
  echo "Cloning OpenFAST repository..."
  git clone https://github.com/OpenFAST/openfast.git openfast
else
  echo "OpenFAST repository already present, skipping clone."
fi

cat <<'DOCKERFILE' > Dockerfile
# Use amd64 to match OpenFAST binaries on Apple Silicon
FROM --platform=linux/amd64 ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential git cmake gfortran liblapack-dev libblas-dev \
    python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
COPY openfast /opt/openfast
WORKDIR /opt/openfast

# Configure & build
RUN cmake -B build -S . -DBUILD_TESTING=ON \
 && cmake --build build --parallel $(nproc) \
 && cmake --install build --prefix /usr/local

# Make test cases available
ENV PATH="/usr/local/bin:${PATH}"
WORKDIR /opt/openfast/build
DOCKERFILE

# Build the image (use amd64 for compatibility on Apple Silicon)
echo "Building Docker image (this may take several minutes)..."
docker build --platform=linux/amd64 -t openfast:latest .

echo "Image built. Starting a container with the current directory mounted to /work."
echo "Run OpenFAST inside the container with: openfast <path/to/case.fst>"
docker run --rm -it --platform=linux/amd64 -v "$PWD":/work -w /work openfast:latest bash
