FROM ubuntu:22.04

RUN sed -i 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list && \
    apt-get update --fix-missing && \
    apt-get install -y g++ && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 sandbox

WORKDIR /sandbox
RUN chown sandbox:sandbox /sandbox

COPY run.sh /run.sh
RUN chmod +x /run.sh

USER sandbox

ENTRYPOINT ["/run.sh"]
