FROM centos/python-38-centos7

USER root

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64
ENV EPICS_BASE /opt/EPICS/epics-base
ENV PATH /opt/EPICS/epics-base/bin/linux-x86_64:$PATH
COPY demo.db /var/ioc/demo.db
COPY supervisord.conf /etc/supervisor/supervisord.conf

RUN mkdir /opt/EPICS 

# general
RUN yum install -y git java-11-openjdk-devel readline libsdc++ &&\
    easy_install supervisor && \
    # install EPICS
    cd /opt/EPICS && \
    git clone --recursive https://github.com/epics-base/epics-base.git && \
    cd epics-base && \
    make

# flash the neighbours
EXPOSE 5064 5065

CMD ["/opt/app-root/bin/supervisord"]