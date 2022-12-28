# Modern URI navigation for VIM

> Double-click->Open. But for VIM. No mouse.

Background: https://sysid.github.io/vimania-uri/

# Key Features
1. Open URIs, html, docx, pptx, jpg, png, mp3, ...
2. Handle almost any URI
3. Paste URLs with human-friendly description

![demo](vimania-uri-demo.png)

## User Interface

> Position cursor on URI and type `go`.

    go

## Link Types
- **local text links**:
    `[foo](second.md)` will be opened inside vim.
    If the target contains line number as in `[foo](second.md:30)`, the line
    will be jumped to.
    Also anchors are supported, for example `[foo](second.md#custom-id)`.
- **URL links**:
    `[google](https://google.com)` will be opened with the OS browser.
- **non text files**:
    if the option `g:vimania-uri#Extensions` is set, non text files will be opened
    via the operating system.
    This behavior is handy when linking to binary documents, for example PDFs.
- **internal links**:
    `[Link Text](#Target)`, will link to the heading `# Target`.
    Following the link will jump to the heading inside vim.
    Currently both github style anchors, all words lowercased and hyphenated,
    and jupyter style anchros, all words hyphenated, are supported.
- **reference style links**:
    for links of the form `[foo][label]`, vimania-uri will lookup the corresponding
    label and open the target referenced there.
- **implicit name links**:
    for links of the form `[foo][]` will use `foo` as the label and then follow
    the logic of reference style links.
- **custom ids via attribute lists**:
    the id a link target can be defined via [attribute lists][attr-lists] of
    the form `{: #someid ...}`.
    This way fixed name references can be defined to prevent links from going
    stale after headings have been changed.
- **local link format of pelican**:
    vimania-uri handles `|filename| ...` and `{filename} ...` links as expected, for
    example `[link](|filename|./second.md)` and
    `[link]({filename}../posts/second.md)`.


#### Usage

In normal model within a markdown document, press `go` on a markdown-link to open it.
If the link is a local file it will be opened in vim (`C-o` will get you back),
otherwise it will be opened via OS (.e.g Web-Broser, Microsoft Office, ...)

The following links can be used (the possible cursor positions are indicated by `^`):

    This [link](https://example.com) will be opened inside the browser.
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^

    This [link](./foo.md) will open `./foo.md` inside vim.
         ^^^^^^^^^^^^^^^^

    This [link](|filename|./foo.md) will open `./foo.md` inside vim.
         ^^^^^^^^^^^^^^^^^^^^^^^^^^

    This $HOME/dir will be opened inside file browser
         ^^^^^^^^^

    This $HOME/dir/present.pptx will open in Powerpoint
         ^^^^^^^^^^^^^^^^^^^^^^


    If `g:vimania-uri_Extensions` is set to `.md, .MD`

    [link](|filename|./example.pdf) will be opened in pdf reader
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Internal linking works, too: to link to the heading Usage, use
    this [link](#usage).
         ^^^^^^^^^^^^^^

    Reference style [links][ref-style-link] will open http://example.com in browser
                    ^^^^^^^^^^^^^^^^^^^^^^^
    [ref-style-link]: http://example.com


The behavior can be configured via the following options:

- `g:vimania_uri_extensions`:
    a comma separated list of file extensions.
    Only files with the given extensions will be opened in vim, all other
    files will be opened via the configured application (using `open` on OSX
    and `xdg-open` on linux).

- `g:vimania_uri_twbm_integration`:
    Boolean flag to configure twbm integration (see below)

---

## Installation
Using [vim-plug](https://github.com/junegunn/vim-plug):
```vim
Plug 'https://github.com/sysid/vimania-uri.git', {'do': 'pip install -r pythonx/requirements.txt --target pythonx'}
  let g:vimania_uri_extensions=['.md','.txt','.rst','.py']
  let g:vimania_uri_twbm_integration=1  # if twbm is installed
```
- vim needs to be configured with python support
- `pip` must be in path in order to install required dependencies into `vimania/pythonx` (no pollution of system python).
- dependencies see [requirements.txt](requirements.txt)


#### Shortcut to create URI
- [UltiSnips](https://github.com/SirVer/ultisnips) for easy URI creation:
```
snippet uri "link/uri for markdown and vimania-uri"
[${1:link}]($1)
endsnippet
```
<br>

## Bookmark Manager Integratiaon
- If [twbm · PyPI](https://pypi.org/project/twbm/) is installed `vimania-uri` pushes URI's to the bookmark database with `goo`.
- Pushed bookmarks have default tag `vimania` in the bookmark-manager db.
- Bookmarks are also removed from bookmark-manager database when removed from markdown file with `dd`

#### Configuration
For bookmark manager [twbm](https://github.com/sysid/twbm) integration the database location needs to be configured:

    export TWBM_DB_URL="sqlite:///$HOME/twbm/bookmarks.db"

    goo (open and save to bookmark DB)
    dd (delete URI containing line from markdown and DB)


## Credits
- inspired by and recommends to use [UltiSnips](https://github.com/SirVer/ultisnips).
- URI handling is based on work of [mdnav](https://github.com/chmp/mdnav)
- Bookmark management is based on work of [jarun/buku](https://github.com/jarun/buku)


## Changelog
[CHANGELOG](https://github.com/sysid/vimania-uri/blob/master/CHANGELOG.rst)

<!-- Badges -->
