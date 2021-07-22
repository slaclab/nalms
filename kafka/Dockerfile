FROM centos:7 as build

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH
ENV KAFKA_HOME=/opt/kafka

RUN  yum install -y wget ${JAVA_BASE}-devel-${JAVA_VERSION} git && \
    cd /opt && \
    git clone https://github.com/linkedin/cruise-control.git && \
    cd cruise-control && \
    git checkout migrate_to_kafka_2_5 && \
    ./gradlew jar :cruise-control:jar && \
    wget https://downloads.apache.org/kafka/2.7.1/kafka_2.13-2.7.1.tgz -O /tmp/kafka_2.13-2.7.1.tgz && \
    tar xvfz /tmp/kafka_2.13-2.7.1.tgz -C /opt && \
    rm /tmp/kafka_2.13-2.7.1.tgz && \
    ln -s /opt/kafka_2.13-2.7.1 ${KAFKA_HOME} && \
    rm -r /tmp/*  

FROM centos:7 as runtime

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH

COPY --from=build ${KAFKA_HOME} $KAFKA_HOME
COPY --from=build  /opt/cruise-control/cruise-control-metrics-reporter/build/libs/* ${KAFKA_HOME}/libs/
COPY scripts/start-kafka.sh /opt/kafka/start-kafka.sh

RUN yum install -y ${JAVA_BASE}-${JAVA_VERSION} openssl && \
    chmod +x /opt/kafka/start-kafka.sh

EXPOSE 9200 9300

CMD /opt/kafka/start-kafka.sh
