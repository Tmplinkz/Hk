FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ="Asia/Kolkata"

# Install system packages – including xz-utils for .tar.xz extraction
RUN apt-get update && apt-get install -y \
    git wget pv jq python3-dev \
    mediainfo gcc libsm6 libxext6 \
    libfontconfig1 libxrender1 libgl1-mesa-glx \
    xz-utils \                      # <--- ADD THIS
 && rm -rf /var/lib/apt/lists/*

# Download and install static FFmpeg from BtbN (includes SVT-AV1)
RUN arch=$(arch | sed 's/aarch64/arm64/' | sed 's/x86_64/64/') && \
    wget -q "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n7.1-latest-linux${arch}-gpl-7.1.tar.xz" && \
    tar -xf ffmpeg-*.tar.xz && \
    cp ffmpeg-*/bin/* /usr/local/bin/ && \
    rm -rf ffmpeg-*

COPY . .

# Install Python dependencies
RUN python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python3 update.py && python3 -m VideoEncoder"]
