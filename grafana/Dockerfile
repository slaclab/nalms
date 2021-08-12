FROM grafana/grafana:7.5.10

ADD ./provisioning/dashboards /etc/grafana/provisioning/dashboards
USER root

RUN mkdir /var/lib/grafana/dashboards && \
    apk add jq curl &&\
    grafana-cli plugins install briangann-datatable-panel

ENV DATASOURCE_DIR=/etc/grafana/provisioning/datasources
ENTRYPOINT []
CMD /run.sh