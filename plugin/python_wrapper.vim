" vim: fdm=marker ts=2 sts=2 sw=2 fdl=0
" convert_string.vim
if g:twvim_debug | echom "-D- Sourcing " expand('<sfile>:p') | endif
let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')

if !has("python3")
  echohl ErrorMsg | echo  "ERROR: vim has to be compiled with +python3 to run this" | echohl None
  finish
endif

" only load it once
if exists('g:vimania_uri_wrapper')
  finish
endif

let g:vimania#PythonScript = expand('<sfile>:r') . '.py'
call TwDebug(printf("Vimania PythonScript: %s", g:vimania#PythonScript))
execute 'py3file ' . g:vimania#PythonScript
"py3file /Users/Q187392/dev/vim/vimania/pythonx/vimania/entrypoint/python_wrapper.py
"py3file /Users/Q187392/dev/vim/vimania/plugin/python_wrapper.py

function! GetURLTitle(url)
  call TwDebug(printf("Vimania args: %s", a:url))
  python3 xMgr.get_url_title(vim.eval('a:url'))
  "call TwDebug(printf("title: %s", g:vimania_url_title))
endfunction
command! -nargs=1 GetURLTitle call GetURLTitle(<f-args>)


function! Vimania(args, save_twbm)
  call TwDebug(printf("Vimania args: %s, save_twbm: %s", a:args, a:save_twbm))
  python3 xMgr.call_handle_md(vim.eval('a:args'), vim.eval('a:save_twbm'))
endfunction
command! -nargs=* Vimania call Vimania(<f-args>)
"nnoremap Q :Vimania /Users/Q187392/dev/vim/vimania/tests/data/test.md 0<CR>

function! VimaniaEdit(args)
  call TwDebug(printf("Vimania args: %s", a:args))
  python3 xMgr.edit_vimania(vim.eval('a:args'))
endfunction
command! -nargs=1 VimaniaEdit call VimaniaEdit(<f-args>)
"nnoremap Q :VimaniaEdit /Users/Q187392/dev/vim/vimania/tests/data/test.md# Working Examples<CR>

function! VimaniaDebug()
  "call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xMgr.debug()
endfunction
command! -nargs=0 VimaniaDebug call VimaniaDebug()
"noremap Q :VimaniaDebug<CR>

function! VimaniaThrowError()
  "call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xMgr.throw_error()
endfunction
command! -nargs=0 VimaniaThrowError call VimaniaThrowError()
"noremap Q :VimaniaDebug<CR>

function! VimaniaDeleteTwbm(args)
  call TwDebug(printf("Vimania args: %s", a:args))
  python3 xMgr.delete_twbm(vim.eval('a:args'))
endfunction
command! -nargs=1 VimaniaDeleteTwbm call VimaniaDeleteTwbm(<f-args>)
"noremap Q :VimaniaDeleteTodo - [ ] todo vimania<CR>

let g:vimania_uri_wrapper = 1
