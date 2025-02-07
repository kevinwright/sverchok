#!/bin/bash

export BLENDER_VERSION=$(blender -b --version | head -n 1 | cut -d' ' -f2 | cut -d'.' -f 1-2)
export BLENDER_ADDON_PATH="$HOME/.config/blender/${BLENDER_VERSION}/scripts/addons"
export BLENDER_CONFIG_PATH="$HOME/.config/blender/${BLENDER_VERSION}/config"

echo "HOME = $HOME"
echo "BLENDER_ADDON_PATH = ${BLENDER_ADDON_PATH}"
echo "BLENDER_CONFIG_PATH = ${BLENDER_CONFIG_PATH}"

echo ""
echo "Installing Addon"
echo "================"

blender -b --python ci-utils/bpy_activate_addon.py --python-exit-code 1 -- $@

echo ""
echo "Launching tests"
echo "==============="

blender -b --python "$BLENDER_ADDON_PATH/sverchok/utils/testing.py" --python-exit-code 1 -- $@

cp "${BLENDER_ADDON_PATH}/sverchok/tests/sverchok_tests.log" "./sverchok_tests_${BLENDER_VERSION}.log" || :
cp -r "${BLENDER_ADDON_PATH}/sverchok/tests/log_files" "./log_files_${BLENDER_VERSION}" || :
