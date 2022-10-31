FROM centos:7 as build

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH

USER root

# install phoebus
RUN yum install -y git maven ${JAVA_BASE}-devel-${JAVA_VERSION} && \
    cd /opt && \
    git clone https://github.com/jbellister-slac/phoebus.git && \
    cd phoebus && \
    mvn install -pl services/alarm-server -am -DskipTests && \
    mkdir /opt/phoebus-build && \
    mv /opt/phoebus/services/alarm-server/target/service-alarm-server-*.jar /opt/phoebus-build/service-alarm-server.jar && \
    mv /opt/phoebus/services/alarm-server/target/lib /opt/phoebus-build/lib && \
    rm -r /opt/phoebus && \
    yum remove -y git maven ${JAVA_BASE}-devel-${JAVA_VERSION}


FROM centos:7 as runtime

COPY cli /opt/nalms/cli
COPY requirements.txt /opt/nalms/requirements.txt
COPY scripts /opt/nalms/scripts
COPY logging.properties /opt/nalms/config/logging.properties

USER root

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH
ENV KAFKA_HOME=/opt/kafka

RUN  yum update -y && \
    yum install -y epel-release && \
    yum install -y python36 && \
    yum install -y python36-setuptools && \
    easy_install-3.6 pip


# general
RUN yum install -y wget ${JAVA_BASE}-${JAVA_VERSION} readline libsdc++ && \
    mkdir /tmp/nalms && \
    mkdir /opt/phoebus && \
    chmod +x /opt/nalms/cli/cli &&\
    mkdir /var/log/nalms && \
    mkdir /var/log/nalms/logs && \
    pip3 install -r /opt/nalms/requirements.txt && \
    wget https://downloads.apache.org/kafka/2.8.2/kafka_2.13-2.8.2.tgz -O /tmp/kafka_2.13-2.8.2.tgz && \
    tar xvfz /tmp/kafka_2.13-2.8.2.tgz -C /opt && \
    rm /tmp/kafka_2.13-2.8.2.tgz && \
    ln -s /opt/kafka_2.13-2.8.2.tgz ${KAFKA_HOME} && \
    rm -r /tmp/* 

COPY --from=build /opt/phoebus-build /opt/phoebus

# set environment
ENV ALARM_SERVER_JAR /opt/phoebus/service-alarm-server.jar
ENV LOGGING_CONFIG_FILE /opt/nalms/config/logging.properties

# prepare to use commands
ENTRYPOINT ["/bin/bash", "/opt/nalms/cli/cli"]
