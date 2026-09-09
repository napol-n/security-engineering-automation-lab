FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       procps \
       iproute2 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd \
    --create-home \
    --shell /bin/bash \
    secsvc

RUN mkdir -p /var/log/secsvc \
    && chown secsvc:secsvc /var/log/secsvc \
    && chmod 750 /var/log/secsvc

RUN mkdir -p /opt/secsvc

COPY service.py /opt/secsvc/service.py

RUN chown root:root /opt/secsvc/service.py \
    && chmod 755 /opt/secsvc/service.py

CMD ["sleep", "infinity"]
