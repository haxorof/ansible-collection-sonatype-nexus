#!/usr/bin/env bash
SAMPLES=(
    "nexus_status_info"
    "nexus_blobstore_file"
    "nexus_read_only"
    "nexus_routing_rule"
    "nexus_security_anonymous"
    "nexus_security_user"
    "nexus_security_user_sources_info"
    "nexus_repository_info"
    "nexus_repository_docker_proxy"
    "nexus_repository_maven_proxy"
)

SAMPLES_PRO=(
    # "nexus_security_user_token"
)

NEXUS_HOST=${NEXUS_HOST:-"nexus.localdomain"}

for SAMPLE in ${SAMPLES[@]}; do
    cd $SAMPLE
    ansible-playbook -c local --extra-vars "nexus_host=$NEXUS_HOST" sample.yml
    cd -
done

if [[ "$1" == "--all" ]]; then
    echo "--> Testing PRO features"
    for SAMPLE in ${SAMPLES_PRO[@]}; do
        cd $SAMPLE
        ansible-playbook -c local --extra-vars "nexus_host=$NEXUS_HOST" sample.yml
        cd -
    done
fi