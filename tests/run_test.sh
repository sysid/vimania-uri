#!/usr/bin/env bash
set +ex
#vim '+Vader!*' && echo Success || echo Failure' && echo Success || echo Failure

source ~/dev/binx/profile/sane_fn.sh

prep-db() {
  echo "-M- Creating vader DB: $(pwd)"
  twpushd "$PROJ_DIR/pythonx/vimania/db"
  [[ -f todos.db  ]] && rm -v todos.db
  alembic upgrade head
  readlink -f todos.db
  cp -v todos.db "$PROJ_DIR/tests/data/vader.db"
  twpopd
}

prep-twbm() {
  echo "-M- Looking for test google entry in twbm to delete if necessary."
  id=$(TWBM_DB_URL=sqlite://///Users/Q187392/vimwiki/buku/bm.db twbm search --np '"www.google.com"')
  if [ ! "$id" == "None" ]; then
    echo "-M- Deleting test google entry in twbm"
    TWBM_DB_URL=sqlite://///Users/Q187392/vimwiki/buku/bm.db twbm delete "$id"
  else
    echo "-M- google test entry not found. All good."
  fi
}

#cp -v data/todos.db.empty data/vader.db

if [ -z "$1" ]; then
    echo "-E- no testfiles given."
    echo "runall: $0 '*'"
    exit 1
fi

################################################################################
# main
################################################################################
prep-db
prep-twbm

TW_VIMANIA_DB_URL=sqlite:///data/vader.db vim -Nu <(cat << EOF
filetype off
set rtp+=~/.vim/plugged/vader.vim
set rtp+=~/.vim/plugged/vim-misc
set rtp+=~/.vim/plugged/scriptease
set rtp+=~/.vim/plugged/vim-textobj-user
set rtp+=~/dev/vim/tw-vim
set rtp+=~/dev/vim/vimania-todos
filetype plugin indent on
syntax enable

let g:twvim_debug = 1
let g:os = 'Darwin'
if g:twvim_debug | echom "-D- Debugging is activated." | endif

" required by tw-vim
let g:twvim_config = {
      \ 'diary_path': '/Users/Q187392/vimwiki/diary',
\ }

" to aovid prompting
set shortmess+=at
"set cmdheight=200
packadd cfilter

EOF) "+Vader! $1" && Green Success || Red Failure

