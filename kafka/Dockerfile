FROM centos:7 as build

RUN yum install -y wget java-11-openjdk-devel git 

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64
RUN cd /opt && \
    git clone https://github.com/linkedin/cruise-control.git && \
    cd cruise-control && \
    git checkout migrate_to_kafka_2_5 && \
    ./gradlew jar :cruise-control:jar 


ENV KAFKA_HOME=/opt/kafka

# Install Java and kafka
ENV PATH $JAVA_HOME/bin:$PATH
RUN wget https://downloads.apache.org/kafka/2.7.1/kafka_2.13-2.7.1.tgz -O /tmp/kafka_2.13-2.7.1.tgz && \
    tar xvfz /tmp/kafka_2.13-2.7.1.tgz -C /opt && \
    rm /tmp/kafka_2.13-2.7.1.tgz && \
    ln -s /opt/kafka_2.13-2.7.1 ${KAFKA_HOME} && \
    rm -r /tmp/*  

FROM centos:7 as runtime

RUN yum install -y java-11-openjdk-devel
ENV KAFKA_HOME=/opt/kafka
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64
ENV PATH $JAVA_HOME/bin:$PATH

COPY --from=build ${KAFKA_HOME} $KAFKA_HOME
COPY --from=build  /opt/cruise-control/cruise-control-metrics-reporter/build/libs/* ${KAFKA_HOME}/libs/

EXPOSE 9200 9300

CMD /opt/kafka/bin/kafka-server-start.sh /opt/kafka/server.properties --override advertised.listeners=${KAFKA_ADVERTISED_LISTENERS} \
    --override listener.security.protocol.map=${KAFKA_LISTENER_SECURITY_PROTOCOL_MAP} --override listeners=${KAFKA_LISTENERS}