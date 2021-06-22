FROM centos/python-38-centos7 as build

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64

USER root

# install phoebus
RUN yum install -y git maven java-11-openjdk-devel && \
    cd /opt && \
    git clone https://github.com/ControlSystemStudio/phoebus.git && \
    cd phoebus && \
    mvn install -pl services/alarm-logger -am -DskipTests

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
    chmod +x /opt/nalms/cli/cli 

COPY --from=build /opt/phoebus/services/alarm-logger/target/service-alarm-logger-*.jar /opt/phoebus/

# set environment
ENV ALARM_LOGGER_PROPERTIES /opt/nalms/config/alarm_logger.properties
ENV ALARM_LOGGER_JAR /opt/phoebus/service-alarm-logger-*.jar
ENV LOGGING_CONFIG_FILE /opt/nalms/config/logging.properties

# prepare to use commands
ENTRYPOINT ["/bin/bash", "/opt/nalms/cli/cli"]