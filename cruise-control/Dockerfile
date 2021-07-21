FROM centos:7 AS build

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64
RUN yum install -y git java-11-openjdk-devel

WORKDIR /opt


RUN git clone https://github.com/linkedin/cruise-control.git \
    && cd cruise-control  \
    && git checkout migrate_to_kafka_2_5 \
    && rm gradle.properties

WORKDIR /opt/cruise-control
COPY gradle.properties /opt/cruise-control/gradle.properties


# Compile and remove leftover directories
RUN ./gradlew jar  \
    && rm -rf cruise-control-core cruise-control-metrics-reporter cruise-control-client \
    && rm config/cruisecontrol.properties 


# Install Cruise Control GUI Frontend
RUN curl -L https://github.com/linkedin/cruise-control-ui/releases/download/v0.1.0/cruise-control-ui.tar.gz \
    -o /tmp/cruise-control-ui.tar.gz \
    && tar zxvf /tmp/cruise-control-ui.tar.gz

# --------------- Final stage ---------------
FROM centos:7
WORKDIR /opt/cruise-control

RUN yum -y install java-11-openjdk-devel && \
    yum clean all -y

COPY --from=build /opt/cruise-control .

# Ensure Cruise Control writable for logs
RUN chmod a+rw -R .

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64

CMD ./kafka-cruise-control-start.sh /opt/cruise-control/config/cruisecontrol.properties