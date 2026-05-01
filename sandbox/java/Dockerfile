FROM eclipse-temurin:17-jdk-alpine

RUN adduser -D -u 1000 sandbox

WORKDIR /sandbox
RUN chown sandbox:sandbox /sandbox

COPY run.sh /run.sh
RUN chmod +x /run.sh

USER sandbox

ENTRYPOINT ["/run.sh"]
