#!/usr/bin/env bash
set -o nounset
set -o pipefail
set -o errexit

source ~/dev/binx/profile/sane_fn.sh

TWBASH_DEBUG=true
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
START_TIME=$SECONDS

hello() {
	echo 'alice bob' | gxargs -n 1 -- echo hi
}

migrate() {
  echo "-M- Migrating DB: $(pwd)"
  [[ -f todos.db  ]] && rm -v todos.db
  alembic upgrade head
  readlink -f todos.db
}

reset-prod() {
  PROD_DB="$HOME/vimwiki/buku/todos.db"
  yes_or_no "Reseeting $PROD_DB" && cp -v todos.db $PROD_DB
  echo "-M- DB reset: $PROD_DB"
}

echo "-M- Start $(date)"
twpushd "$SCRIPT_DIR/.."

"$@"  # dispatch on _parameter_to_change_

twpopd
echo "-M- End: $(($SECONDS - $START_TIME))"
exit 0
