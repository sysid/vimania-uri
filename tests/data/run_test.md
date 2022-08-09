# Working Examples
from codebase:
file:///\%(\K[\/.]*\)\+': ':call TextobjUriOpen()',
file:///\%(\k[\/.]*\)\+': ':call TextobjUriOpen()',  mit digits

## Plugin Config
```vim
URIPatternAdd! xxx://\%(\k[\/.]*\)\+ :echo\ "%s"
URIPatternAdd! xxx://\%(\([^()]\+\)\) :echom\ "%s"

URIPatternAdd! xxx://\%(\([^()]\+\)\) :silent\ !open\ "%s"
```
xxx://xxx/xxx.pdf
xxx://$HOME/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf
[xxx](xxx://$HOME/dev/vim/vim-textobj-uri/test/xxx/xxx.pdf)

file2:///Volumes/DE-Org/DE-3/DE-39
[D: DE-39 department](file2:///Volumes/DE-Org/DE-3/DE-39)

### gx
- must be in test directory cd ./test
[xxx](xxx/xxx.pdf)




## Plugin Source
file:///Users/Q187392/xxx/xxx/xxx.pdf
[file: xxx](file:///Users/Q187392/xxx/xxx/xxx.pdf)

some text http://www.slashdot.org/ some more text

!!! dash in path not working
