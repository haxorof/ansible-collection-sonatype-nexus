#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
NEXUS_HOST="${NEXUS_HOST:-nexus.localdomain}"
VENV_PATH="${VENV_PATH:-$SCRIPT_DIR/../.linuxenv}"
DEBUG_LOG_PATH="$SCRIPT_DIR"
export DEBUG_LOG_PATH

USAGE='Usage: run_samples.sh [--all | <sample_name>]'

SAMPLES=(
    "workaround"
    "nexus_compat_check"
    "nexus_capabilities"
    "nexus_blobstore_file"
    "nexus_cleanup_policies_internal"
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
    "nexus_script"
    "nexus_script_run"
    "nexus_security_anonymous"
    "nexus_security_ldap"
    "nexus_security_ldap_info"
    "nexus_security_ldap_order"
    "nexus_security_user_sources_info"
    "nexus_security_user"
    "nexus_status_info"
)

SAMPLES_PRO=(
    "nexus_cleanup_policies"
    "nexus_http"
    "nexus_security_user_token"
)

ALL_SAMPLES=("${SAMPLES[@]}" "${SAMPLES_PRO[@]}")

activate_venv() {
    local activate_script="$VENV_PATH/bin/activate"
    if [[ ! -f "$activate_script" ]]; then
        echo "ERROR: virtualenv activate script not found at '$activate_script'"
        exit 2
    fi
    # shellcheck source=/dev/null
    . "$activate_script"
}

run_test() {
    local in_path="$1"
    echo ""
    echo "#############"
    echo "# BEGIN ##### $in_path"

    pushd "$in_path" > /dev/null || return 1

    export NEXUS_URL="http://$NEXUS_HOST:8081"
    export NEXUS_VALIDATE_CERTS=False
    export NEXUS_USERNAME=admin
    export NEXUS_PASSWORD=admin123
    export ANSIBLE_FORCE_COLOR=True

    ansible-playbook -c local sample.yml

    echo "# END ####### $(pwd)"
    echo "#############"
    echo ""

    popd > /dev/null || return 1
}

is_known_sample() {
    local needle="$1"
    for sample in "${ALL_SAMPLES[@]}"; do
        [[ "$sample" == "$needle" ]] && return 0
    done
    return 1
}

run_all_standard() {
    echo "--> Testing all non-PRO samples"
    for sample in "${SAMPLES[@]}"; do
        run_test "$sample"
    done
}

run_all_pro() {
    echo "--> Testing PRO features"
    for sample in "${SAMPLES_PRO[@]}"; do
        run_test "$sample"
    done
}

run_all() {
    run_all_standard
    run_all_pro
}

run_one() {
    local sample="$1"
    if ! is_known_sample "$sample"; then
        echo "Unknown sample '$sample'."
        echo "$USAGE"
        exit 1
    fi

    if [[ " ${SAMPLES_PRO[*]} " == *" $sample "* ]]; then
        echo "--> Testing PRO sample '$sample'"
    else
        echo "--> Testing sample '$sample'"
    fi

    run_test "$sample"
}

main() {
    activate_venv

    local selected_sample="${1:-}"
    if [[ -z "$selected_sample" ]]; then
        run_all_standard
        return
    fi

    if [[ "$selected_sample" == "--all" ]]; then
        run_all
        return
    fi

    run_one "$selected_sample"
}

main "${1:-}"

