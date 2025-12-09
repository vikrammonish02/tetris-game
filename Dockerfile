# Multi-stage build for OpenFAST v4.0 with Python 3.11 and FastAPI

# Stage 1: build OpenFAST from source
FROM ubuntu:22.04 AS openfast-builder

ARG OPENFAST_VERSION=v4.0.0

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       build-essential \
       git \
       ca-certificates \
       cmake \
       gfortran \
       libblas-dev \
       liblapack-dev \
       libfftw3-dev \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/openfast

RUN git clone --branch ${OPENFAST_VERSION} --depth 1 https://github.com/OpenFAST/openfast.git . \
    && cmake -S . -B build \
        -DBUILD_SHARED_LIBS=OFF \
        -DBUILD_OPENFAST=ON \
        -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build --target openfast --config Release -- -j"$(nproc)"


# Stage 2: runtime with Python 3.11, FastAPI, and OpenFAST binary
FROM python:3.11-slim AS runtime

ENV PATH="/usr/local/bin:${PATH}"

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       libgfortran5 \
       libgomp1 \
       libblas3 \
       liblapack3 \
       libfftw3-double3 \
    && rm -rf /var/lib/apt/lists/*

# Copy OpenFAST executable from builder
COPY --from=openfast-builder /tmp/openfast/build/glue-codes/openfast/openfast /usr/local/bin/openfast

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "simulation_api:app", "--host", "0.0.0.0", "--port", "8000"]
