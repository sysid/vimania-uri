#!/usr/bin/env bash
XXX_DB="$1"

_RESET="\e[0m"
_RED="\e[91m"
_GREEN="\e[92m"

Red() {
  printf "${_RED}%s${_RESET}\n" "$@"
}
Green() {
  printf "${_GREEN}%s${_RESET}\n" "$@"
}

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") xxx_db

Create database for xxx vim-plugin.
EOF
  exit
}

if [ -z "$XXX_DB" ]; then
  usage
fi

if [ -f "$XXX_DB" ]; then
  Red "-E- $XXX_DB does already exist, please remove to proceed."
  exit 1
fi

create_db() {
  sqlite3 "$XXX_DB" <<____HERE
CREATE TABLE xxx_todos (
        id INTEGER NOT NULL,
        todo VARCHAR NOT NULL,
        metadata VARCHAR,
        tags VARCHAR,
        "desc" VARCHAR,
        flags INTEGER,
        last_update_ts DATETIME DEFAULT (CURRENT_TIMESTAMP),
        created_at DATETIME,
        PRIMARY KEY (id)
);
____HERE
}

################################################################################
# main
################################################################################
create_db

echo "-M- Created $XXX_DB."
