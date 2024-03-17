#!/usr/bin/env bash
# Simple steps to setup Nexus 3 to run samples with.
# Note! nexus.localdomain must be set in your etc/hosts to where your local test instance will be available.
NEXUS_HOST=${NEXUS_HOST:-"nexus.localdomain"}
docker pull sonatype/nexus3
# Default password would be admin123
docker run -d -p 8081:8081 --name nexus -v nexus_volume:/nexus-data -e NEXUS_SECURITY_RANDOMPASSWORD=false sonatype/nexus3
timeout 120 bash -c 'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://$NEXUS_HOST:8081/service/rest/v1/status/writable)" != "200" ]]; do sleep 5; done' || false
