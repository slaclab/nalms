FROM grafana/grafana

ADD ./provisioning/dashboards /etc/grafana/provisioning/dashboards
ADD ./config.ini /etc/grafana/config.ini
ADD ./dashboards /var/lib/grafana/dashboards

#RUN mkdir /opt/nalms
ADD scripts/start-grafana.sh /opt/nalms/
ADD scripts/update-dashboards.sh /opt/nalms/

CMD bash /opt/nalms/start-grafana.sh