# Build Stage

FROM python:3.12-alpine AS builder

# using uv pacakge manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# install build dependencies (alpine uses apk)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libpcap-dev

WORKDIR /app

# install python dependencies from requirements 
# use a persistent cache for fast rebuilds
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache-dir -r requirements.txt


# Production Runner Stage
FROM python:3.12-alpine AS runner

WORKDIR /app

# install runtime system dependencies 
# required for libpcap, Scapy, and network utilities
RUN apk add --no-cache \
    libpcap \
    iproute2 \
    iw \
    wireless-tools \
    tcpdump 

# copy over Python site packages and binaries from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# copy app source code and entrypoint
COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# default command (requires root privileges and host network mode)
CMD ["python", "src/capture.py"]