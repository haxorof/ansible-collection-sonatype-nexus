#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
NEXUS_HOST=${NEXUS_HOST:-"nexus.localdomain"}
VENV_PATH=${VENV_PATH:-$SCRIPT_DIR/../.linuxenv}

function run_test() {
    _in_path=$1
    cd $_in_path > /dev/null
    echo ""
    echo "#############"
    echo "# BEGIN ##### $(pwd)"
    ansible-playbook -c local --extra-vars "nexus_url=http://$NEXUS_HOST:8081" --extra-vars "nexus_username=admin" --extra-vars "nexus_password=admin123" sample.yml
    echo "# END ####### $(pwd)"
    echo "#############"
    echo ""
    cd - > /dev/null
}

SAMPLES=(
	"nexus_capabilities"
    "nexus_blobstore_file"
    "nexus_cleanup_policies"
    "nexus_email"
    "nexus_license"
    "nexus_read_only"
    "nexus_repository_info"
    "nexus_repository_docker_hosted"
    "nexus_repository_docker_proxy"
    "nexus_repository_docker_group"
    "nexus_repository_go_proxy"
    "nexus_repository_go_group"
    "nexus_repository_helm_hosted"
    "nexus_repository_helm_proxy"
    "nexus_repository_maven_hosted"
    "nexus_repository_maven_proxy"
    "nexus_repository_maven_group"
    "nexus_repository_npm_hosted"
    "nexus_repository_npm_proxy"
    "nexus_repository_npm_group"
    "nexus_repository_nuget_hosted"
    "nexus_repository_nuget_proxy"
    "nexus_repository_nuget_group"
    "nexus_repository_p2_proxy"
    "nexus_repository_pypi_hosted"
    "nexus_repository_pypi_proxy"
    "nexus_repository_pypi_group"
    "nexus_repository_raw_hosted"
    "nexus_repository_raw_proxy"
    "nexus_repository_raw_group"
    "nexus_repository_rubygems_hosted"
    "nexus_repository_rubygems_proxy"
    "nexus_repository_rubygems_group"
    "nexus_roles_info"
    "nexus_roles"
    "nexus_routing_rule"
    "nexus_script_info"
    "nexus_script_run"
    "nexus_script"
    "nexus_security_anonymous"
    "nexus_security_ldap_info"
    "nexus_security_ldap_order"
    "nexus_security_ldap"
    "nexus_security_user_sources_info"
    "nexus_security_user"
    "nexus_status_info"
)

SAMPLES_PRO=(
    "nexus_http"
    "nexus_security_user_token"
)

. $VENV_PATH/bin/activate

for SAMPLE in ${SAMPLES[@]}; do
    run_test $SAMPLE
done

if [[ "${1:-''}" == "--all" ]]; then
    echo "--> Testing PRO features"
    for SAMPLE in ${SAMPLES_PRO[@]}; do
        run_test $SAMPLE
    done
fi
