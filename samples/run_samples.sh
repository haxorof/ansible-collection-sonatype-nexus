#!/usr/bin/env bash

SAMPLES=(
    "nexus_read_only"
    "nexus_routing_rule"
    "nexus_security_anonymous"
    "nexus_security_user"
    "nexus_security_user_sources_info"
    "nexus_status_info"
    "nexus_repository_info"
)

for SAMPLE in ${SAMPLES[@]}; do
    cd $SAMPLE
    ansible-playbook -c local sample.yml
    cd -
done