FROM centos:7 AS build

ENV CC_VERSION=2.5.59
ENV JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk
#ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64
RUN yum -y install git java-1.8.0-openjdk-devel

WORKDIR /opt

RUN git clone --branch ${CC_VERSION} https://github.com/linkedin/cruise-control.git 

WORKDIR /opt/cruise-control

# Compile and remove leftover directories
RUN ./gradlew jar :cruise-control:jar  \
    && rm -rf cruise-control-core cruise-control-metrics-reporter cruise-control-client \
    && rm config/cruisecontrol.properties

# Install Cruise Control GUI Frontend
RUN curl -L https://github.com/linkedin/cruise-control-ui/releases/download/v0.1.0/cruise-control-ui.tar.gz \
    -o /tmp/cruise-control-ui.tar.gz \
    && tar zxvf /tmp/cruise-control-ui.tar.gz

# --------------- Final stage ---------------
FROM centos:7
WORKDIR /opt/cruise-control

RUN yum -y install java-1.8.0-openjdk && \
    yum clean all -y

COPY --from=build /opt/cruise-control .

# Ensure Cruise Control writable for logs
RUN chmod a+rw -R .

CMD ./kafka-cruise-control-start.sh config/cruisecontrol.properties