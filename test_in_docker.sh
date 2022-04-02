#!/bin/bash

set -e

if [[ -f sverchok.zip ]]
then
    echo " "
    echo "=========================="
    echo "       Blender 2.93       "
    echo "=========================="

    docker pull ghcr.io/kevinwright/sverchok-testing-image:2.93

    docker run \
    --name sverchok-testing \
    --workdir /github/workspace \
    --entrypoint /github/workspace/ci-utils/start-ci-test.sh \
    --rm \
    -v "$(pwd)":"/github/workspace" \
    ghcr.io/kevinwright/sverchok-testing-image:2.93

    echo " "
    echo "=========================="
    echo "       Blender 3.0        "
    echo "=========================="

    docker pull ghcr.io/kevinwright/sverchok-testing-image:3.0

    docker run \
    --name sverchok-testing \
    --workdir /github/workspace \
    --entrypoint /github/workspace/ci-utils/start-ci-test.sh \
    --rm \
    -v "$(pwd)":"/github/workspace" \
    ghcr.io/kevinwright/sverchok-testing-image:3.0

    # echo " "
    # echo "=========================="
    # echo "       Blender 3.1        "
    # echo "=========================="
    
    # docker pull ghcr.io/kevinwright/sverchok-testing-image:3.1

    # docker run \
    # --name sverchok-testing \
    # --workdir /github/workspace \
    # --entrypoint /github/workspace/ci-utils/start-ci-test.sh \
    # --rm \
    # -v "$(pwd)":"/github/workspace" \
    # ghcr.io/kevinwright/sverchok-testing-image:3.1
else    
    echo "sverchok.zip doesn't exist, run build_zip.sh before testing"
fi    