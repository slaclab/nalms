#!/bin/bash

# Updates local dashboard configurations by retrieving
# the new version from a Grafana instance.
#
# The script assumes that basic authentication is configured
# (change the login credentials with `LOGIN`).
#
# DASHBOARD_DIRECTORY represents the path to the directory
# where the JSON files corresponding to the dashboards exist.
# The default location is relative to the execution of the
# script.
#
# URL specifies the URL of the Grafana instance.
#

sleep 10 

set -o errexit

readonly URL=${URL:-"http://localhost:3000"}
readonly LOGIN=${LOGIN:-"admin:admin"}
readonly DASHBOARDS_DIRECTORY=${DASHBOARDS_DIRECTORY:-"./grafana/dashboards"}


main() {
  local dashboards=$(list_dashboards)
  local dashboard_json

  show_config

  for dashboard in $dashboards; do
    dashboard_json=$(get_dashboard "$dashboard")

    if [[ -z "$dashboard_json" ]]; then
      echo "ERROR:
  Couldn't retrieve dashboard $dashboard.
      "
      exit 1
    fi

    echo "$dashboard_json" >$DASHBOARDS_DIRECTORY/$dashboard.json
  done
}


# Shows the global environment variables that have been configured
# for this run.
show_config() {
  echo "INFO:
  Starting dashboard extraction.
  
  URL:                  $URL
  LOGIN:                $LOGIN
  DASHBOARDS_DIRECTORY: $DASHBOARDS_DIRECTORY
  "
}


# Retrieves a dashboard from the database of dashboards.
get_dashboard() {
  local dashboard=$1

  if [[ -z "$dashboard" ]]; then
    echo "ERROR:
  A dashboard must be specified.
  "
    exit 1
  fi

  curl \
    --silent \
    --user "$LOGIN" \
    $URL/api/dashboards/db/$dashboard |
    jq '.dashboard | .id = null'
}


# lists all the dashboards available.
#
list_dashboards() {
  curl \
    --silent \
    --user "$LOGIN" \
    $URL/api/search |
    jq -r '.[] | select(.type == "dash-db") | .uri' |
    cut -d '/' -f2
}

main "$@"