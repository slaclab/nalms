# Use the elasticsearch image (centos7)
FROM docker.elastic.co/elasticsearch/elasticsearch:7.17.5@sha256:76344d5f89b13147743db0487eb76b03a7f9f0cd55abe8ab887069711f2ee27d

COPY scripts/init_es.sh /opt/nalms/
COPY scripts/create_alarm_template.sh /opt/nalms/
RUN chmod +x /opt/nalms/init_es.sh  && \
    chmod +x /opt/nalms/create_alarm_template.sh

CMD ["/opt/nalms/init_es.sh"]