#!/usr/bin/env bash

helm upgrade --install postgres oci://registry-1.docker.io/bitnamicharts/postgresql \
    --set auth.postgresPassword=hotbot \
    --set auth.database=hotbot \
    --set auth.username=hotbot \
    --set auth.password=hotbot \
    --set auth.rootPassword=hotbot