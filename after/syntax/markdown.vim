" Vim syntax file
if exists("b:twtodo_loaded")
  finish
endif

" use arbitrary mathc ID: -1
call matchadd('Conceal', '%[0-9]\+%', 0, -1, {'conceal': ''})

" Custom conceal (not working)
"syntax match todoCheckbox "\[\ \]" conceal cchar=%
"syntax match todoCheckbox "\[x\]" conceal cchar=%
"
let b:twtodo_loaded = "twtodo"
""
""hi def link todoCheckbox Todo
"hi Conceal guibg=NONE
"
"setlocal cole=1
