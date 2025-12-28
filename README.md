# Ansible Collection - haxorof.sonatype_nexus

[![GitHub tag](https://img.shields.io/github/tag/haxorof/ansible-collection-sonatype-nexus)](https://github.com/haxorof/ansible-collection-sonatype-nexus)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://github.com/haxorof/ansible-collection-sonatype-nexus/blob/master/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/haxorof/ansible-collection-sonatype-nexus/ci.yml)](https://github.com/haxorof/ansible-collection-sonatype-nexus/actions/workflows/ci.yml)

Ansible collection for managing Sonatype Nexus Repository Manager 3.x via its REST API.

## Features

### OSS Features

<!-- * Manage read-only system status
* Manage routing rules
* Manage users
* Retrieve user sources
* Manage anonymous access
* Check status
* List repositories
* Manage repositories
* Manage blob stores
-->
TODO

### PRO Features

<!--
* Manage HTTP settings
* Manage user tokes capability
-->
TODO

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
