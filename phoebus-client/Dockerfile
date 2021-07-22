FROM centos:7 as build

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH

USER root

COPY pom.xml /opt/nalms/pom.xml

# install phoebus
RUN yum install -y git maven ${JAVA_BASE}-devel-${JAVA_VERSION} && \
    cd /opt && \
    git clone https://github.com/ControlSystemStudio/phoebus.git && \
    cd phoebus && \
    rm phoebus-product/pom.xml && \
    mv /opt/nalms/pom.xml phoebus-product/pom.xml && \
    mvn install -pl phoebus-product -am -DskipTests 

FROM centos:7 as runtime

COPY . /opt/nalms/
USER root

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH $JAVA_HOME/bin:$PATH

RUN yum install -y ${JAVA_BASE}-${JAVA_VERSION} mesa-libGL xfonts-100dpi xfonts-encodings \
    xfonts-utils openjfx libopenjfx-jni libopenjfx-java gtk3-devel dbus && \
    chmod +x /opt/nalms/run.sh

COPY --from=build /opt/phoebus /opt/phoebus/

CMD /opt/nalms/run.sh