FROM centos:7

# general
RUN yum install -y wget

# Install Java
RUN yum install -y \
   java-11-openjdk 

ENV JAVA_HOME /usr/lib/jvm/jre-11-openjdk

# Install Kafka
ENV KAFKA_HOME=/opt/kafka

RUN wget https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz -O /tmp/kafka_2.13-2.8.0.tgz && \
    tar xvfz /tmp/kafka_2.13-2.8.0.tgz -C /opt && \
    rm /tmp/kafka_2.13-2.8.0.tgz && \
    ln -s /opt/kafka_2.13-2.8.0 ${KAFKA_HOME} && \
    rm -r /tmp/* 

COPY config/server.properties ${KAFKA_HOME}/server.properties

CMD ["/opt/kafka/bin/kafka-server-start.sh /opt/kafka/server.properties"]