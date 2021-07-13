FROM centos/python-38-centos7 as build

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64

USER root

# install phoebus
RUN yum install -y git maven java-11-openjdk-devel && \
    cd /opt && \
    git clone https://github.com/ControlSystemStudio/phoebus.git && \
    cd phoebus && \
    mvn install

FROM centos/python-38-centos7 as runtime

COPY . /opt/nalms/
USER root

RUN yum install -y java-11-openjdk-devel mesa-libGL xfonts-100dpi xfonts-encodings \
    xfonts-utils openjfx libopenjfx-jni libopenjfx-java gtk3-devel dbus && \
    chmod +x /opt/nalms/run.sh

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64
ENV PATH $JAVA_HOME/bin:$PATH

COPY --from=build /opt/phoebus /opt/phoebus/


CMD /opt/nalms/run.sh