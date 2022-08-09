#!/usr/bin/env bash
set -o nounset
set -o pipefail
set -o errexit

TWBASH_DEBUG=true
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
START_TIME=$SECONDS
temp_file=$(mktemp)
VIMANIA_PYTHON_VERSION=${VIMANIA_PYTHON_VERSION:-python3.10}

dev() {
  echo "-M- python version: $VIMANIA_PYTHON_VERSION"
  TARGET_DIR="$(pipenv --where)/pythonx"
  SOURCE_DIR="$(pipenv --venv)/lib/${VIMANIA_PYTHON_VERSION}/site-packages/"
  pushd "$PROJ_DIR" || exit 1
  rsync -avu --exclude '__pycache__' --exclude '_virtualenv*' --exclude '_distutils_hack' --exclude '_pytest' "$SOURCE_DIR" "$TARGET_DIR"
  popd || exit 1
}

prod() {
  TARGET_DIR="$(find-vimania-plugin)/pythonx"
  if [ "$TARGET_DIR" == "/pythonx" ]; then
    echo "-E- Could not find the vimenia plugin path"
    return 1
  fi
  SOURCE_DIR="$HOME/.local/pipx/venvs/vimania/lib/python3.9/site-packages"
  if ! pipx list | grep vimania 2>&1 >/dev/null; then
    echo "-E- vimenia not found. Have you installed it with pipx?"
    return 1
  fi
  if [ ! -d "$SOURCE_DIR" ]; then
    echo "-E- $SOURCE_DIR not found. Have you installed vimania it with pipx?"
    return 1
  fi
  echo "$TARGET_DIR"
  echo "$SOURCE_DIR"
#  pushd "$PROJ_DIR" || exit 1
#  rsync -avu --exclude '__pycache__' --exclude '_virtualenv*' --exclude '_distutils_hack' --exclude '_pytest' "$SOURCE_DIR" "$TARGET_DIR"
#  popd || exit 1
}

find-vimania-plugin(){
  vim -V2"${temp_file}" -c ':q' --not-a-term > /dev/null
  PLUGIN=$(grep 'plugin/vimania.vim$' "${temp_file}" | grep finished | cut -f 3 -d ' ')
  PLUGIN=${PLUGIN%%plugin/vimania.vim}
  echo $PLUGIN
}


echo "-M- Start $(date)"
################################################################################
"$@"  # dispatch on _parameter_to_change_
################################################################################
rm "${temp_file}"
echo "-M- End: $(($SECONDS - $START_TIME))"
exit 0
