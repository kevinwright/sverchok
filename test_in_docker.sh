#!/bin/bash

set -e

if [[ -f sverchok.zip ]]
then
    docker run \
    --name sverchok-testing \
    --workdir /github/workspace \
    --rm \
    -v "$(pwd)":"/github/workspace" \
    ghcr.io/kevinwright/sverchok-testing-image:latest
else    
    echo "sverchok.zip doesn't exist, run build_zip.sh before testing"
fi    