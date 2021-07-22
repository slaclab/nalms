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
    mvn install -pl services/alarm-logger -am -DskipTests

FROM centos/python-38-centos7 as runtime

COPY cli /opt/nalms/cli
USER root

ENV JAVA_VERSION java-11-openjdk-11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_HOME /usr/lib/jvm/${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH

# general
RUN yum install -y git maven ${JAVA_VERSION} readline libsdc++\
    mkdir /tmp/nalms && \
    mkdir /opt/phoebus && \
    cd /opt/nalms && \
    mkdir /opt/nalms/config && \
    chmod +x /opt/nalms/cli/cli && \ 
    mkdir /var/log/nalms && \
    mkdir /var/log/nalms/logs

COPY --from=build /opt/phoebus/services/alarm-logger/target/service-alarm-logger-*.jar /opt/phoebus/

# set environment
ENV ALARM_LOGGER_PROPERTIES /opt/nalms/config/alarm_logger.properties
ENV ALARM_LOGGER_JAR /opt/phoebus/service-alarm-logger-*.jar
ENV LOGGING_CONFIG_FILE /opt/nalms/config/logging.properties

# prepare to use commands
ENTRYPOINT ["/bin/bash", "/opt/nalms/cli/cli"]