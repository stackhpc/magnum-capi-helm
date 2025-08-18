# magnum-capi-helm plugin.sh - Devstack extras script to install magnum

# Save trace setting
XTRACE=$(set +o | grep xtrace)
set -o xtrace

echo_summary "magnum's plugin.sh was called..."
source $DEST/magnum-capi-helm/devstack/lib/magnum-capi-helm
(set -o posix; set)

if is_service_enabled magnum-api magnum-cond; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing helm binary"
        install_helm
        echo_summary "Installing magnum-capi-helm"
        install_magnum_capi_helm
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        if is_service_enabled k8s-capi; then
            echo_summary "Installing Azimuth CAPI addon provider"
            install_azimuth_cluster_api_addon_provider
            echo_summary "Installing Azimuth CAPI janitor OpenStack"
            install_azimuth_capi_janitor_openstack
        fi
    fi
fi

# Restore xtrace
$XTRACE
