FROM centos:7 AS build


ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH ${JAVA_HOME}/bin:$PATH

COPY gradle.properties /tmp/cruise-control/gradle.properties

WORKDIR /opt

#    && rm gradle.properties \
#    && cp /tmp/cruise-control/gradle.properties gradle.properties \

RUN yum install -y git ${JAVA_BASE}-devel-${JAVA_VERSION} && \
    git clone https://github.com/linkedin/cruise-control.git \
    && cd cruise-control  \
    && git checkout migrate_to_kafka_2_5 \
    && ./gradlew jar \
    && rm -rf cruise-control-core cruise-control-metrics-reporter cruise-control-client \
    && rm config/cruisecontrol.properties \
    && curl -L https://github.com/linkedin/cruise-control-ui/releases/download/v0.1.0/cruise-control-ui.tar.gz \
    -o /tmp/cruise-control-ui.tar.gz \
    && tar zxvf /tmp/cruise-control-ui.tar.gz


FROM centos:7 as runtime
WORKDIR /opt/cruise-control

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH ${JAVA_HOME}/bin:$PATH
ENV CRUISE_CONTROL_PROPERTIES /opt/cruise-control/config/cruisecontrol.properties

COPY --from=build /opt/cruise-control .
COPY config.csv /opt/cruise-control/cruise-control-ui/dist/static/config.csv
COPY start-cruise-control.sh /opt/cruise-control

RUN yum -y install ${JAVA_BASE}-${JAVA_VERSION} && \
    yum clean all -y && \
    chmod +x /opt/cruise-control/start-cruise-control.sh && \
    chmod a+rw -R .

CMD ./start-cruise-control.sh