FROM centos/python-38-centos7 as build

ENV JAVA_VERSION java-11-openjdk-11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_HOME /usr/lib/jvm/${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH

USER root

# install phoebus
RUN yum install -y git maven ${JAVA_VERSION} && \
    cd /opt && \
    git clone https://github.com/ControlSystemStudio/phoebus.git && \
    cd phoebus && \
    mvn install -pl services/alarm-server -am -DskipTests && \
    mkdir /opt/phoebus-build && \
    mv /opt/phoebus/services/alarm-server/target/service-alarm-server-*.jar /opt/phoebus-build/service-alarm-server.jar && \
    mv /opt/phoebus/services/alarm-server/target/lib /opt/phoebus-build/lib && \
    rm -r /opt/phoebus


FROM centos/python-38-centos7 as runtime

COPY cli /opt/nalms/cli
COPY requirements.txt /opt/nalms/requirements.txt
COPY scripts /opt/nalms/scripts

USER root

ENV JAVA_VERSION java-11-openjdk-11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_HOME /usr/lib/jvm/${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH
ENV KAFKA_HOME=/opt/kafka

# general
RUN yum install -y ${JAVA_VERSION}} readline libsdc++\
    mkdir /tmp/nalms && \
    mkdir /opt/phoebus && \
    chmod +x /opt/nalms/cli/cli &&\
    mkdir /var/log/nalms && \
    mkdir /var/log/nalms/logs && \
    pip install -r /opt/nalms/requirements.txt && \
    wget https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz -O /tmp/kafka_2.13-2.8.0.tgz && \
    tar xvfz /tmp/kafka_2.13-2.8.0.tgz -C /opt && \
    rm /tmp/kafka_2.13-2.8.0.tgz && \
    ln -s /opt/kafka_2.13-2.8.0 ${KAFKA_HOME} && \
    rm -r /tmp/* 

COPY --from=build /opt/phoebus-build /opt/phoebus

# set environment
ENV ALARM_SERVER_PROPERTIES /opt/nalms/config/alarm_server.properties
ENV ALARM_SERVER_JAR /opt/phoebus/service-alarm-server.jar
ENV LOGGING_CONFIG_FILE /opt/nalms/config/logging.properties

# prepare to use commands
ENTRYPOINT ["/bin/bash", "/opt/nalms/cli/cli"]