FROM grafana/grafana

ADD ./provisioning/dashboards /etc/grafana/provisioning/dashboards
ADD ./config.ini /etc/grafana/config.ini
COPY ./dashboards/alarm_logs_dashboard.json /opt/nalms/alarm_logs_dashboard.json

COPY scripts/start-grafana.sh /opt/nalms/start-grafana.sh
COPY scripts/update-dashboards.sh /opt/nalms/update-dashboards.sh
COPY scripts/create-datasource-file.sh /opt/nalms/create-datasource-file.sh

USER root

RUN mkdir /var/lib/grafana/dashboards && \
    apk add jq curl &&\
    chmod +x /opt/nalms/start-grafana.sh && \
    chmod +x /opt/nalms/update-dashboards.sh && \
    chmod +x /opt/nalms/create-datasource-file.sh && \
    grafana-cli plugins install briangann-datatable-panel

ENV DATASOURCE_DIR=/etc/grafana/provisioning/datasources
ENV DASHBOARD_TEMPLATE=/opt/nalms/alarm_logs_dashboard.json
ENV DASHBOARD_DIR=/var/lib/grafana/dashboards
ENV DASHBOARDS_DIRECTORY=/var/lib/grafana/dashboards

ENTRYPOINT []
CMD /opt/nalms/start-grafana.sh