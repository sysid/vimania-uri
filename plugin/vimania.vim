if exists('g:loaded_vimania_todos')
    finish
endif

if g:twvim_debug | echom "-D- Sourcing " expand('<sfile>:p') | endif
let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')

augroup Vimania-Todos
 autocmd!
 autocmd BufRead *.md call VimaniaHandleTodos("read")
 autocmd BufWritePre *.md call VimaniaHandleTodos("write")
 "autocmd TextYankPost *.md echom v:event

 " line must have todo-id: %99%
 " event must be dlete: d
 " event must not be visual (visual: do not delete in DB, useful for moving tasks)
 autocmd TextYankPost *.md
    \ if len(v:event['regcontents']) == 1 && v:event['regcontents'][0] =~? '%\d\+%' && v:event['operator'] == 'd' && ! v:event['visual']
    \ | call VimaniaDeleteTodo(v:event['regcontents'][0], expand('%:p'))
    \ | endif
augroup END

let g:loaded_vimania_todos = 1
