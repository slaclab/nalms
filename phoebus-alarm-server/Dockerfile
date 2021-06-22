FROM centos/python-38-centos7 as build

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64

USER root

# install phoebus
RUN yum install -y git maven java-11-openjdk-devel && \
    cd /opt && \
    git clone https://github.com/ControlSystemStudio/phoebus.git && \
    cd phoebus && \
    mvn install -pl services/alarm-server -am -DskipTests 

FROM centos/python-38-centos7 as runtime

COPY . /opt/nalms/
USER root
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64

# general
RUN yum install -y git maven java-11-openjdk-devel readliine libsdc++\
    tmux && \
    mkdir /tmp/nalms && \
    mkdir /opt/phoebus && \
    # set up python
    python -m pip install -r /opt/nalms/requirements.txt && \
    cd /opt/nalms && \
    python -m pip install . && \
    chmod +x /opt/nalms/cli/cli && \
    # install EPICS
    mkdir /opt/EPICS && \
    cd /opt/EPICS && \
    git clone --recursive https://github.com/epics-base/epics-base.git && \
    cd epics-base && \
    make

# Install Kafka
ENV KAFKA_HOME=/opt/kafka

RUN wget https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz -O /tmp/kafka_2.13-2.8.0.tgz && \
    tar xvfz /tmp/kafka_2.13-2.8.0.tgz -C /opt && \
    rm /tmp/kafka_2.13-2.8.0.tgz && \
    ln -s /opt/kafka_2.13-2.8.0 ${KAFKA_HOME} && \
    rm -r /tmp/* 

COPY --from=build /opt/phoebus/services/alarm-server/target/lib /opt/phoebus/lib

# set environment
ENV ALARM_SERVER_PROPERTIES /opt/nalms/config/alarm_server.properties
ENV ALARM_SERVER_JAR /opt/phoebus/service-alarm-server-*.jar
ENV LOGGING_CONFIG_FILE /opt/nalms/config/logging.properties
ENV EPICS_BASE /opt/EPICS/epics-base
ENV TEMPLATE_FILE /opt/nalms/files/sevrpv.db

# prepare to use commands
ENTRYPOINT ["/bin/bash", "/opt/nalms/cli/cli"]