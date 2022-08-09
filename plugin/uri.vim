if exists('g:loaded_vimania_uri')
    finish
endif
if g:twvim_debug | echom "-D- Sourcing " expand('<sfile>:p') | endif
let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')

function! s:HandleMd(save_twbm)
  python3 xMgr.call_handle_md2(vim.eval('a:save_twbm'))
endfunction

" opens the URI no saving action triggered
nnoremap <Plug>HandleMd :<C-u>call <sid>HandleMd(0)<CR>
command! HandleMd :call <sid>HandleMd(0)
" opens the URI and saves it to URI DB from twbm module (python)
nnoremap <Plug>HandleMdSave :<C-u>call <sid>HandleMd(1)<CR>
command! HandleMdSave :call <sid>HandleMd(1)

if ! hasmapto('<Plug>HandleMd', 'n')
    nmap go <Plug>HandleMd
endif

if ! hasmapto('<Plug>HandleMdSave', 'n')
    nmap goo <Plug>HandleMdSave
endif

augroup Vimania-Uri
 autocmd!
" removes URL (pattern) from twbm
 autocmd TextYankPost *.md
    \ if len(v:event['regcontents']) == 1 && v:event['regcontents'][0] =~? 'http[s]\=://' && v:event['operator'] == 'd' && ! v:event['visual']
    \ | call VimaniaDeleteTwbm(v:event['regcontents'][0])
    \ | endif
augroup END

let g:loaded_vimania_uri = 1
