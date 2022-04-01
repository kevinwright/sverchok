#!/bin/bash

# If your blender is not available as just "blender" command, then you need
# to specify path to blender when running this script, e.g.
#
# $ BLENDER=~/soft/blender-2.79/blender ./run_tests.sh
#

set -e

mkdir -p /tmp/zipbuild/sverchok
rsync -av . /tmp/zipbuild/sverchok --exclude '.git**'
pushd /tmp/zipbuild
zip -r sverchok.zip sverchok
popd
cp /tmp/zipbuild/sverchok.zip .