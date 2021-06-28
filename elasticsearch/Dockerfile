# Use the elasticsearch image (centos7)

FROM docker.elastic.co/elasticsearch/elasticsearch:6.8.16@sha256:37994c16cea5a3c89195e77c63967f2910747bef18b272c3229da40afdc68f2c

COPY config config
COPY scripts/init_es.sh /opt/nalms/
COPY scripts/create_alarm_template.sh /opt/nalms/
RUN chmod +x /opt/nalms/init_es.sh  && \
    chmod +x /opt/nalms/create_alarm_template.sh

CMD ["/opt/nalms/init_es.sh"]