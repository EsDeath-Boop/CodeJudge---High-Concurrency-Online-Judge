FROM python:3.11-slim

RUN useradd -m -u 1000 sandbox

WORKDIR /sandbox
RUN chown sandbox:sandbox /sandbox

COPY run.sh /run.sh
RUN chmod +x /run.sh

USER sandbox

ENTRYPOINT ["/run.sh"]
