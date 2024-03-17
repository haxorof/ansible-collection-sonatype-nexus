#!/usr/bin/env bash
# Simple steps to setup Nexus 3 to run samples with.
# Note! nexus.localdomain must be set in your etc/hosts to where your local test instance will be available.
docker pull sonatype/nexus3
docker stop nexus
docker rm nexus --volumes
docker volume rm nexus_volume
# Default password would be admin123
docker run -d -p 8081:8081 --name nexus -v nexus_volume:/nexus-data -e NEXUS_SECURITY_RANDOMPASSWORD=false sonatype/nexus3
timeout 300 bash -c 'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://nexus.localdomain:8081/service/rest/v1/status/writable)" != "200" ]]; do sleep 5; done' || false
