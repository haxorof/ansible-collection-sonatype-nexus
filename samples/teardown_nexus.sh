#!/usr/bin/env bash
docker stop nexus
docker rm nexus --volumes
#docker volume rm nexus_volume
