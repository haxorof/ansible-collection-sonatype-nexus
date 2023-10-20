# Ansible Collection - haxorof.sonatype_nexus

Ansible collection for managing Sonatype Nexus Repository Manager 3.x via its REST API.

## Features

### OSS Features

* Manage read-only system status
* Manage routing rules
* Manage users
  * Limitations: Not possible to change password
* Retrieve user sources
* Manage anonymous access
* Check status
* List repositories
* Manage repositories:
  * Limited to:
    * Docker proxy
    * Maven proxy

### PRO Features

* Manage user tokes capability

## Installation

Different was of installing this collection are listed below.

### Requirements File

Create `requirements.yml` file and provide required version of the collection:

```yaml
collections:
  - name: https://github.com/haxorof/ansible-collection-sonatype-nexus.git
    type: git
    version: main
```

Run ansible-galaxy command with `requirements.yml` file as argument:

```bash
ansible-galaxy collection install -r requirements.yml --force
```

### Command-Line One-Liner

```bash
ansible-galaxy collection install git+https://github.com/haxorof/ansible-collection-sonatype-nexus.git
```
