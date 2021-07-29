FROM centos:7 as build

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH

USER root

# install phoebus
RUN yum install -y git maven ${JAVA_BASE}-devel-${JAVA_VERSION} && \
    cd /opt && \
    git clone https://github.com/ControlSystemStudio/phoebus.git && \
    cd phoebus && \
    mvn install -pl services/alarm-logger -am -DskipTests && \
    mkdir /opt/phoebus-build && \
    mv /opt/phoebus/services/alarm-logger/target/service-alarm-logger-*.jar /opt/phoebus-build/service-alarm-logger.jar && \
    rm -r /opt/phoebus && \
    yum remove -y ${JAVA_BASE}-devel-${JAVA_VERSION} maven git


FROM centos:7 as runtime

COPY logger.properties /opt/nalms/config/alarm_logger.properties
COPY logging.properties /opt/nalms/config/logging.properties
COPY cli /opt/nalms/cli
USER root

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH

# general
RUN yum install -y ${JAVA_BASE}-${JAVA_VERSION} \
    mkdir /tmp/nalms && \
    mkdir /opt/phoebus && \
    cd /opt/nalms && \
    chmod +x /opt/nalms/cli/cli && \ 
    mkdir /var/log/nalms && \
    mkdir /var/log/nalms/logs

COPY --from=build /opt/phoebus-build /opt/phoebus

# set environment
ENV ALARM_LOGGER_PROPERTIES /opt/nalms/config/alarm_logger.properties
ENV ALARM_LOGGER_JAR /opt/phoebus/service-alarm-logger-*.jar
ENV LOGGING_CONFIG_FILE /opt/nalms/config/logging.properties

# prepare to use commands
ENTRYPOINT ["/bin/bash", "/opt/nalms/cli/cli"]