# Ansible Collection - haxorof.sonatype_nexus

[![GitHub tag](https://img.shields.io/github/tag/haxorof/ansible-collection-sonatype-nexus)](https://github.com/haxorof/ansible-collection-sonatype-nexus)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://github.com/haxorof/ansible-collection-sonatype-nexus/blob/master/LICENSE)

Ansible collection for managing Sonatype Nexus Repository Manager 3.x via its REST API.

## Features

### Community/OSS Features

* Manage blob stores (limited)
  * file
* Manage capabilities
* Manage e-mail settings
* Manage license
* Manage read-only system status
* Manage repositories (limited)
  * docker
  * go
  * helm
  * maven
  * npm
  * nuget
  * p2
  * pypi
  * raw
  * rubygems
* Manage roles
* Manage routing rules
* Manage and run scripts
* Manage users
* Manage anonymous access
* Manage LDAP settings
* Manage users
* Retrieve user sources
* Check status
* Manage tasks

### PRO Features

* Manage cleanup policies
* Manage HTTP settings
* Manage user tokens capability

### Other Features

* Compatibility check between collection and Sonatype Nexus

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
