# Use the elasticsearch image (centos7)
FROM docker.elastic.co/elasticsearch/elasticsearch:6.8.22@sha256:abb31b525b19f5b0e47c71a8db54dbf3860c58c7e15a572d2919f6bad53e947e

COPY scripts/init_es.sh /opt/nalms/
COPY scripts/create_alarm_template.sh /opt/nalms/
RUN chmod +x /opt/nalms/init_es.sh  && \
    chmod +x /opt/nalms/create_alarm_template.sh

CMD ["/opt/nalms/init_es.sh"]