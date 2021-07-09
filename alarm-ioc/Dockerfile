FROM centos/python-38-centos7

USER root

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-11.0.11.0.9-1.el7_9.x86_64
ENV EPICS_BASE /opt/EPICS/epics-base
ENV PATH /opt/EPICS/epics-base/bin/linux-x86_64:$PATH

# Template file
ENV TEMPLATE_FILE /opt/nalms/sevrpv.db

# Config file
ENV CONFIG_FILE /opt/nalms/alarm.xml
ENV IOC_DIR /opt/nalms/ioc

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY requirements.txt /opt/nalms/requirements.txt
COPY run.sh /opt/nalms/run.sh
COPY sevrpv.db /opt/nalms/sevrpv.db
COPY create_soft_iocs.py /opt/nalms/create_soft_iocs.py

RUN mkdir /opt/EPICS && \
    mkdir /opt/nalms/ioc

# general
RUN yum install -y git java-11-openjdk-devel readline libsdc++ &&\
    easy_install supervisor && \
    # install EPICS
    cd /opt/EPICS && \
    git clone --recursive https://github.com/epics-base/epics-base.git && \
    cd epics-base && \
    make && \
    # set up python
    python -m pip install -r /opt/nalms/requirements.txt && \
    chmod +x /opt/nalms/run.sh 

# flash the neighbours
EXPOSE 5064 5065

CMD ["/opt/app-root/bin/supervisord"]