FROM node:12-alpine as build

RUN cd /tmp && \
    apk add git yarn && \
    git clone --branch undefined-rendering https://github.com/jacquelinegarrahan/grafana-datatable-panel.git && \
    cd grafana-datatable-panel && \
    yarn install && \
    yarn build

FROM grafana/grafana:7.5.10 as runtime

ADD ./provisioning/dashboards /etc/grafana/provisioning/dashboards
USER root
COPY --from=build /tmp/grafana-datatable-panel /var/lib/grafana/plugins/grafana-datatable-panel

RUN mkdir /var/lib/grafana/dashboards 

ENV GF_AUTH_DISABLE_LOGIN_FORM "true"
ENV GF_AUTH_ANONYMOUS_ENABLED "true"
ENV GF_AUTH_ANONYMOUS_ORG_ROLE "Admin"
ENV DATASOURCE_DIR=/etc/grafana/provisioning/datasources

ENTRYPOINT []
CMD /run.sh