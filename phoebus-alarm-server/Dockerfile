FROM debian:bullseye-slim as build

ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

USER root

# install phoebus
RUN apt-get update && \
    apt-get install -y git maven openjdk-11-jdk && \
    cd /opt && \
    git clone https://github.com/jbellister-slac/phoebus.git && \
    cd phoebus && \
    git fetch --tags && \
    git checkout tags/v4.7.2-1.1.0 && \
    mvn install -pl services/alarm-server -am -DskipTests && \
    mkdir /opt/phoebus-build && \
    mv /opt/phoebus/services/alarm-server/target/service-alarm-server-*.jar /opt/phoebus-build/service-alarm-server.jar && \
    mv /opt/phoebus/services/alarm-server/target/lib /opt/phoebus-build/lib && \
    rm -r /opt/phoebus && \
    apt-get remove -y openjdk-11-jdk maven git


FROM debian:bullseye-slim as runtime

COPY cli /opt/nalms/cli
COPY requirements.txt /opt/nalms/requirements.txt
COPY scripts /opt/nalms/scripts
COPY logging.properties /opt/nalms/config/logging.properties

USER root

ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH
ENV KAFKA_HOME=/opt/kafka
ENV BUNDLED_KAFKA_VERSION 2.13-3.3.2


# general
RUN apt-get update && \
    apt-get install -y openjdk-11-jre curl iputils-ping wget python3-pip && \
    mkdir /tmp/nalms && \
    mkdir /opt/phoebus && \
    chmod +x /opt/nalms/cli/cli &&\
    mkdir /var/log/nalms && \
    mkdir /var/log/nalms/logs && \
    pip3 install -r /opt/nalms/requirements.txt && \
    wget https://downloads.apache.org/kafka/3.3.2/kafka_${BUNDLED_KAFKA_VERSION}.tgz -O /tmp/kafka_${BUNDLED_KAFKA_VERSION}.tgz && \
    tar xvfz /tmp/kafka_${BUNDLED_KAFKA_VERSION}.tgz -C /opt && \
    rm /tmp/kafka_${BUNDLED_KAFKA_VERSION}.tgz && \
    ln -s /opt/kafka_${BUNDLED_KAFKA_VERSION} ${KAFKA_HOME} && \
    rm -r /tmp/* 

COPY --from=build /opt/phoebus-build /opt/phoebus

# set environment
ENV ALARM_SERVER_JAR /opt/phoebus/service-alarm-server.jar
ENV LOGGING_CONFIG_FILE /opt/nalms/config/logging.properties

# prepare to use commands
ENTRYPOINT ["/bin/bash", "/opt/nalms/cli/cli"]
