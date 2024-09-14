# Testing

## Prerequisites

* VirtualBox
* Vagrant

## Setup Environment

1. Setup Ansible and virtual environment: ../samples/setup_ansible.sh
2. Apply Molecule Vagrant plugin patch

    ```shell
    # https://github.com/ansible-community/molecule-plugins/issues/193

    mkdir ../.linuxenv/lib/python3.11/site-packages/molecule_plugins/vagrant/schema
    wget -O ../.linuxenv/lib/python3.11/site-packages/molecule_plugins/vagrant/schema/driver.json https://raw.githubusercontent.com/apatard/molecule-plugins/vagrant-schema/src/molecule_plugins/vagrant/schema/driver.json
    ```

3. Set environment if vagrant private key is in different location than usual:

    ```shell
    export VAGRANT_PRIVATE_KEY=/some/different/location/.ssh/vagrant.key.rsa
    ```

4. nexus.domainlocal in /etc/hosts

    ```text
    192.168.56.56   nexus.localdomain
    ```

## Activate virtual environment and run tests

```shell
. ../.linuxenv/bin/activate
molecule test
```
