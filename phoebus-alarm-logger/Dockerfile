FROM debian:bookworm-slim as build

ENV JAVA_BASE java-17-openjdk
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

USER root

# install phoebus
RUN apt-get update && \
    apt-get install -y git maven openjdk-17-jdk && \
    cd /tmp && \
    git clone https://github.com/ControlSystemStudio/phoebus.git && \
    cd phoebus && \
    git fetch --tags && \
    git checkout tags/v5.0.0 && \
    mvn install -pl services/alarm-logger -am -DskipTests && \
    mkdir /opt/phoebus-build && \
    mv /tmp/phoebus/services/alarm-logger/target/service-alarm-logger-*.jar /opt/phoebus-build/service-alarm-logger.jar && \
    rm -r /tmp/phoebus && \
    apt-get remove -y openjdk-17-jdk maven git


FROM debian:bookworm-slim as runtime

COPY logging.properties /opt/nalms/config/logging.properties
COPY cli /opt/nalms/cli
USER root

ENV JAVA_BASE java-17-openjdk
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

# general
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk curl iputils-ping && \
    mkdir /tmp/nalms && \
    mkdir /opt/phoebus && \
    cd /opt/nalms && \
    chmod +x /opt/nalms/cli/cli && \ 
    mkdir /var/log/nalms && \
    mkdir /var/log/nalms/logs

COPY --from=build /opt/phoebus-build /opt/phoebus

# set environment
ENV ALARM_LOGGER_JAR /opt/phoebus/service-alarm-logger.jar
ENV LOGGING_CONFIG_FILE /opt/nalms/config/logging.properties

# prepare to use commands
ENTRYPOINT ["/bin/bash", "/opt/nalms/cli/cli"]
