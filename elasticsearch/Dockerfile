FROM centos:centos7

EXPOSE 9200
USER 0


ENV JAVA_HOME /usr/lib/jvm/jre-11-openjdk
COPY files/elasticsearch.repo /etc/yum.repos.d/elasticsearch.repo 
RUN mkdir /opt/nalms
COPY scripts/create_alarm_template.sh /opt/nalms/
COPY scripts/init_es.sh /opt/nalms/

# install the RPMs in a separate step so it can be cached
RUN rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch && \
  yum install -y --setopt=tsflags=nodocs \
                java-11-openjdk  \
                elasticsearch && \
  yum clean all && \
  chmod +x /opt/nalms/create_alarm_template.sh && \
  chmod +x /opt/nalms/init_es.sh


ENV ES_HOST localhost
ENV ES_PORT 9200
ENV ES_HOME /usr/share/elasticsearch

WORKDIR ${HOME}
USER 999
CMD ["/opt/nalms/init_es.sh"]