# Ansible Collection - haxorof.sonatype_nexus

Ansible collection for managing Sonatype Nexus Repository Manager 3.x via its REST API.

## Features

* Manage read-only system status
* Manage routing rules
* Manage users

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
