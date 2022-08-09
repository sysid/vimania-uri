" vim: fdm=marker ts=2 sts=2 sw=2 fdl=0

" todo: remove: prevents reloading ??
"if exists('g:loaded_textobj_uri')
" finish
"endif

if g:twvim_debug | echom "-D- Sourcing " expand('<sfile>:p') | endif
let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')


call textobj#user#plugin('uri', {
      \ 'uri': {
      \ '*select-a-function*': 'textobj#uri#selecturi_a',
      \ 'select-a': 'au',
      \ '*select-i-function*': 'textobj#uri#selecturi_i',
      \ 'select-i': 'iu',
      \ },
      \ })

let g:textobj_uri_positioning_patterns_asciidoc = [
      \ '\%(http\|link\|xref\|mailto\|image:\?\|include:\):\zs[^[]\+\[[^]]*\]',
      \ '<<\zs[^,>]\+\%(,[^>]\+\)\?>>',
      \ ]

let g:textobj_uri_positioning_patterns_markdown = [
      \ '\[[^]]*\](\zs[^)]\+)',
      \ "\\[[^]]*\\]:\\s*<\\?\\zs[^\\t ]\\+\\%(\\s\\+\\([('\"]\\)[^('\"]*\\1\\)\\?",
      \ ]

let g:textobj_uri_positioning_patterns_org = [
      \ '\[\{2}\zs[^][]*\%(\]\[[^][]*\)\?\]\{2}',
      \ ]

" Default:
let g:textobj_uri_positioning_patterns = [
      \ ]

let g:textobj_uri_patterns_markdown = {
      \ '\[[^]]\+\] \?\[\([^]]\+\)\]': "/\\V\\^\\s\\*\\[%s\\]:\\s",
      \ '\[\([^]]\+\)\] \?\[\]': "/\\V\\^\\s\\*\\[%s\\]:\\s",
      \ }

" Default:
""      \ '\%(http\|https\|ftp\):\/\/[a-zA-Z0-9:@_-]*\%(\.[a-zA-Z0-9][a-zA-Z0-9-]*\)*\%(:\d\+\)\?\%(\/[a-zA-Z0-9_\/.\-+%#?&=;@$,!''*~]*\)\?': ':call TextobjUriOpen()',
""      \ 'file:///\%(\k[\/.]*\)\+': ':call TextobjUriOpen()',
""      \ 'file://\%(\([^)]\+\)\)': ':call TextobjUriOpen()',
let g:textobj_uri_patterns = {
      \ '\%(http\|https\|ftp\):\/\/[a-zA-Z0-9:@_-]*\%(\.[a-zA-Z0-9][a-zA-Z0-9-]*\)*\%(:\d\+\)\?\%(\/[a-zA-Z0-9_\/.\-+%#?&=;@$,!''*~]*\)\?': ':call Vimania(g:textobj_uri, a:save_twbm)',
      \ 'mailto:[a-zA-Z0-9._]\+@[a-zA-Z0-9-]*\%(\.[a-zA-Z0-9][a-zA-Z0-9-]*\)*': ':call TextobjUriOpen()',
      \ 'file://\%(\([^)]\+\)\)': ':call TextobjUriOpen()',
      \ 'vm::\%(\([^)]\+\)\)': ':call Vimania(g:textobj_uri, a:save_twbm)',
      \ 'vim::\%(\([^)]\+\)\)': ':call VimaniaEdit(g:textobj_uri)',
      \ 'todo::\%(\([^)]\+\)\)': ':call VimaniaTodo(g:textobj_uri, expand("%:p"))',
      \ '\%((\(.\+\))\)': ':call TextobjUriOpen()',
      \ }

let g:textobj_uri_search_timeout = 100

function! TextobjUriOpen()
        let p = resolve(expand(g:textobj_uri, ':p'))
        call TwDebug(printf('TextobjUriOpen:textobj_uri %s fullpath: %s', g:textobj_uri, p))

        call TwDebug(printf('xxxx TextobjUriOpen:textobj_uri %s fullpath: %s', g:textobj_uri, g:textobj_uri[0:0]))

        " if startswith # then search in file
        if g:textobj_uri[0:0] ==# '#'
            "silent execute '/'.printf('^%s', g:textobj_uri)
            silent execute '/^'.g:textobj_uri

      elseif executable('open-cli')
        call TwDebug(printf('TextobjUriOpen: %s %s &', 'open-cli', shellescape(p)))
        silent! call system(printf('%s %s &', 'open-cli', shellescape(g:textobj_uri)))
    elseif executable('xdg-open')
        call TwDebug(printf('TextobjUriOpen: %s %s &', 'xdg-open', shellescape(p)))
        silent! call system(printf('%s %s &', 'xdg-open', shellescape(g:textobj_uri)))
    elseif executable('open')
        call TwDebug(printf('TextobjUriOpen: %s %s &', 'open', shellescape(p)))
        silent! call system(printf('%s %s &', 'open', shellescape(p)))
    else
      echoerr "No OS launcher found."
    endif
endfunction

function! s:extract_uri(trailing_whitespace)
  let orig_pos = getpos('.')
  let positioning_patterns = []
  for ft in split(&ft, '\.')
    if exists('g:textobj_uri_positioning_patterns_'.ft)
      call extend(positioning_patterns, eval('g:textobj_uri_positioning_patterns_'.ft))
    endif
  endfor
  call extend(positioning_patterns, g:textobj_uri_positioning_patterns)
  for ppattern in positioning_patterns
    let nozs_ppattern = substitute(ppattern, '\\zs', '', 'g')
    call setpos('.', orig_pos)
    if search(nozs_ppattern, 'ceW', orig_pos[1], g:textobj_uri_search_timeout) == 0
      call setpos('.', orig_pos)
      continue
    endif
    let end_pos = getpos('.')

    if search(nozs_ppattern, 'bcW', orig_pos[1], g:textobj_uri_search_timeout) == 0
      call setpos('.', orig_pos)
      continue
    endif
    let start_pos = getpos('.')

    if search(ppattern, 'cW', orig_pos[1], g:textobj_uri_search_timeout) == 0
      call setpos('.', orig_pos)
      continue
    endif

    let uri_pos = getpos('.')
    if start_pos[2] > orig_pos[2] || end_pos[2] < orig_pos[2] || start_pos[2] > uri_pos[2] || end_pos[2] < uri_pos[2]
      call setpos('.', orig_pos)
      continue
    endif
    let orig_pos = uri_pos
    break
  endfor
  let patterns = copy(g:textobj_uri_patterns)
  for ft in split(&ft, '\.')
    if exists('g:textobj_uri_patterns_'.ft)
      call extend(patterns, eval('g:textobj_uri_patterns_'.ft), 'force')
    endif
  endfor
  for pattern in keys(patterns)
    call setpos('.', orig_pos)
    let tmp_pattern = pattern
    if a:trailing_whitespace
      let tmp_pattern = pattern . '\s*'
    endif
    if search(tmp_pattern, 'ceW', orig_pos[1], g:textobj_uri_search_timeout) == 0
      call setpos('.', orig_pos)
      continue
    endif
    let end_pos = getpos('.')

    if search(tmp_pattern, 'bcW', orig_pos[1], g:textobj_uri_search_timeout) == 0
      call setpos('.', orig_pos)
      continue
    endif
    let start_pos = getpos('.')
    if start_pos[2] > orig_pos[2] || end_pos[2] < orig_pos[2]
      " cursor is not within the pattern
      call setpos('.', orig_pos)
      continue
    endif
    return [[pattern, patterns[pattern]], 'v', start_pos, end_pos]
  endfor
endfunction

function! textobj#uri#selecturi_a()
  let res = s:extract_uri(1)
  if len(res) == 4
    return res[1:]
  endif
endfunction

function! textobj#uri#selecturi_i()
  let res = s:extract_uri(0)
  if len(res) == 4
    return res[1:]
  endif
endfunction

function! textobj#uri#add_pattern(bang, pattern, ...)
  if a:bang
    if a:0 > 1
      for ft in a:000[1:]
        exec 'let g:textobj_uri__patterns_'.ft.' = {}'
      endfor
    else
      let g:textobj_uri_patterns = {}
    endif
  endif
  if a:0
    if a:0 > 1
      for ft in a:000[1:]
        if ! exists('g:textobj_uri_patterns_'.ft)
          exec ':let g:textobj_uri_patterns_'.ft.' = {}'
        endif
        call extend(eval('g:textobj_uri_patterns_'.ft), {a:pattern : a:000[0]})
      endfor
    else
      let g:textobj_uri_patterns[a:pattern] = a:000[0]
    endif
  else
    let g:textobj_uri_patterns[a:pattern] = ''
  endif
endfunction

function! textobj#uri#add_positioning_pattern(bang, ppattern, ...)
  if a:bang
    if a:0
      for ft in a:000
        exec 'let g:textobj_uri_positioning_patterns_'.ft.' = []'
      endfor
    else
      let g:textobj_uri_positioning_patterns = []
    endif
  endif
  if a:0
    for ft in a:000
      if ! exists('g:textobj_uri_positioning_patterns_'.ft)
        exec ':let g:textobj_uri_positioning_patterns_'.ft.' = []'
      endif
      call add(eval('g:textobj_uri_positioning_patterns_'.ft), a:ppattern)
    endfor
  else
    call add(g:textobj_uri_positioning_patterns, a:ppattern)
  endif
endfunction

function! textobj#uri#open_uri(save_twbm)
  " open_uri:res: [['vm::\%(\([^)]\+\)\)', ':call Vimania(g:textobj_uri)'], 'v', [0, 4, 16, 0], [0, 4, 40, 0]]
  let res = s:extract_uri(0)
    call TwDebug(printf('open_uri:res: %s save_twbm: %s', res, a:save_twbm))

  let uri = ''
  if len(res) == 4
    " extract submatches
    let uri_match = matchlist(getline('.')[res[2][2]-1:res[3][2]-1], res[0][0])
        " ['vm::http://www.vimania.tw', 'http://www.vimania.tw', '', '', '', '', '', '', '', '']
        call TwDebug(printf('open_uri:uri_match: %s', uri_match))
    if uri_match[1] != ''
      " use first submatch as URI
      let uri = uri_match[1]
    else
      let uri = uri_match[0]
    endif
    " remove trailing single quote
    let uri = substitute(uri, '''$', '', '')
    let handler = substitute(res[0][1], '%s', fnameescape(uri), 'g')

    if len(handler)
        let g:textobj_uri = uri
        " open_uri:handler: :call Vimania(g:textobj_uri) http://www.vimania.tw
        call TwDebug(printf('open_uri:handler: %s %s', handler, uri))

      if index([':', '/', '?'], handler[0]) != -1
        exec handler
      else
        exec 'normal' handler
      endif

      unlet g:textobj_uri
    else
      throw "No handler specified"
    endif

  endif
  return uri
endfunction
let g:loaded_textobj_uri = 1
