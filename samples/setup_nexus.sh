#!/usr/bin/env bash
# Simple steps to setup Nexus 3 to run samples with.
# Note! nexus.localdomain must be set in your etc/hosts to where your local test instance will be available.
NEXUS_HOST=${NEXUS_HOST:-"nexus.localdomain"}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-""}
if [[ "${DOCKER_REGISTRY}" != "" && "${DOCKER_REGISTRY: -1}" != "/" ]]; then
    DOCKER_REGISTRY="${DOCKER_REGISTRY}/"
fi
IMAGE_TAG=${IMAGE_TAG:-"latest"}
IMAGE="${DOCKER_REGISTRY}sonatype/nexus3:$IMAGE_TAG"
echo "-> Using image $IMAGE"
docker pull ${IMAGE}
# Default password would be admin123
docker rm nexus
docker volume rm nexus
docker run -d -p 8081:8081 --name nexus -v nexus:/nexus-data -e INSTALL4J_ADD_VM_PARAMS="-Dnexus.scripts.allowCreation=true -Djava.util.prefs.userRoot=/nexus-data/javaprefs" -e NEXUS_SECURITY_RANDOMPASSWORD=false ${IMAGE}
if [[ "$?" == "0" ]]; then
    echo "-> Starting Nexus and waiting for it to complete within 1 minutes..."
    timeout 60 bash -c 'while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://$NEXUS_HOST:8081/service/rest/v1/status/writable)" != "200" ]]; do sleep 5; done' || false
fi
