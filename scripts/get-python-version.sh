#!/usr/bin/env bash

set -o nounset
set -o pipefail
set -o errexit

TWBASH_DEBUG=true
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
START_TIME=$SECONDS

temp_file=$(mktemp)


get_python_version() {
	vim -c "redir! > $temp_file" -c 'py3 import sys; from pprint import pprint; print(f"VIM Python Version:\n{sys.version}\n"); pprint(sys.path)' -c ':q'
	cat $temp_file
}

################################################################################
get_python_version
#"$@"  # dispatch on _parameter_to_change_
################################################################################
rm "${temp_file}"
exit 0