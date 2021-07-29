FROM centos:7

USER root

ENV JAVA_VERSION 11.0.12.0.7-0.el7_9.x86_64
ENV JAVA_BASE java-11-openjdk
ENV JAVA_HOME /usr/lib/jvm/${JAVA_BASE}-${JAVA_VERSION}
ENV PATH ${JAVA_HOME}/bin:$PATH
ENV EPICS_BASE /opt/EPICS/epics-base
ENV EPICS_BASE_VERSION R7.0.3.1
ENV PATH /opt/EPICS/epics-base/bin/linux-x86_64:$PATH
COPY heart_of_gold.db /var/ioc/heart_of_gold.db
COPY supervisord.conf /etc/supervisor/supervisord.conf

RUN mkdir /opt/EPICS 

# general
RUN yum install -y git ${JAVA_BASE}-${JAVA_VERSION} readline libsdc++ supervisor make gcc perl &&\
    yum groupinstall -y 'Development Tools' && \
    # install EPICS
    cd /opt/EPICS && \
    git clone --recursive --branch $EPICS_BASE_VERSION https://github.com/epics-base/epics-base.git && \
    cd epics-base && \
    make

# flash the neighbours
EXPOSE 5064 5065

CMD ["/opt/app-root/bin/supervisord"]