FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        iputils-ping \
        python3 \
        python3-flask \
        sqlite3 \
        tini \
        util-linux \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash aegisnet \
    && mkdir -p /opt/aegisnet/app /srv/aegisnet/files /srv/aegisnet/public /var/lib/aegisnet /run/aegisnet

WORKDIR /opt/aegisnet

COPY app/ /opt/aegisnet/app/
COPY entrypoint.sh /entrypoint.sh

RUN chmod 0755 /entrypoint.sh \
    && chown -R root:root /opt/aegisnet /srv/aegisnet /var/lib/aegisnet /run/aegisnet

EXPOSE 8080

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
