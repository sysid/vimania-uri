# Vimania: URI navigation for VIM markdown

[![PyPI Version][pypi-image]][pypi-url]

> handle URI's like double-clicking, but with VIM shortcut

Key features:
1. open/navigate arbitrary URIs in markdown files
2. Save interesting URI seamless in bookmark manager: [twbm](https://github.com/sysid/twbm).
3. Can handle almost every kind of URI


## Super simple user interface
Position cursor in normal mode on URI and just say `go`.

    go (open URL, directories, files, ...)
    goo (open and save to bookmark DB)
    dd (delete URI containing line from markdown and DB)

- **local text links**:
    `[foo](second.md)` will be opened inside vim.
    If the target contains line number as in `[foo](second.md:30)`, the line
    will be jumped to.
    Also anchors are supported, for example `[foo](second.md#custom-id)`.
- **URL links**:
    `[google](https://google.com)` will be opened with the OS browser.
- **non text files**:
    if the option `g:mdnav#Extensions` is set, non text files will be opened
    via the operating system.
    This behavior is handy when linking to binary documents, for example PDFs.
- **internal links**:
    `[Link Text](#Target)`, will link to the heading `# Target`.
    Following the link will jump to the heading inside vim.
    Currently both github style anchors, all words lowercased and hyphenated,
    and jupyter style anchros, all words hyphenated, are supported.
- **reference style links**:
    for links of the form `[foo][label]`, mdnav will lookup the corresponding
    label and open the target referenced there.
    This mechanism works will all link targets.
- **implicit name links**:
    for links of the form `[foo][]` will use `foo` as the label and then follow
    the logic of reference style links.
- **custom ids via attribute lists**:
    the id a link target can be defined via [attribute lists][attr-lists] of
    the form `{: #someid ...}`.
    This way fixed name references can be defined to prevent links from going
    stale after headings have been changed.
- **local link format of pelican**:
    mdnav handles `|filename| ...` and `{filename} ...` links as expected, for
    example `[link](|filename|./second.md)` and
    `[link]({filename}../posts/second.md)`.

Note, all links above are functional with vim and vimania installed.
Vimania's URI handling is inspired by [mdnav][mdnav].

[label]: https://google.com
[foo]: https://wikipedia.org
[fml]: https://github.com/prashanthellina/follow-markdown-links
[attr-lists]: https://pythonhosted.org/Markdown/extensions/attr_list.html
[mdnav]: https://github.com/chmp/mdnav


### Usage

Inside normal model with an open markdown document, press `go` on a markdown link to open it.
If the link is a local file it will be opened in vim (`C-o` will get you back),
otherwise it will be opened via OS (.e.g Web-Broser, Microsoft Office, ...)

The following links can be used (the possible cursor positions are indicated by `^`):

    This [link](https://example.com) will be opened inside the browser.
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^

    This [link](./foo.md) will open `./foo.md` inside vim.
         ^^^^^^^^^^^^^^^^

    This [link](|filename|./foo.md) will open `./foo.md` inside vim.
         ^^^^^^^^^^^^^^^^^^^^^^^^^^

    If `g:mdnav#Extensions` is set to `.md, .MD`, enter will open
    `example.pdf` inside the default PDF reader for this
    [link](|filename|./example.pdf).
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Internal linking works, too: to link to the heading Usage, use
    this [link](#usage).
         ^^^^^^^^^^^^^^

    Reference style [links][ref-style-link] work too.
                    ^^^^^^^^^^^^^^^^^^^^^^^

    [ref-style-link]: http://example.com


The behavior can be configured via the following options:

- `g:vimania_uri_extensions`:
    a comma separated list of file extensions.
    Only file s with the given extensions will be opened in vim, all other
    files will be opened via the configured application (using `open` on OSX
    and `xdg-open` on linux).
    This option may be useful to link to non-text documents, say PDF files.
- `g:vimania_uri_twbm_integration`:
    Boolean flag to configure twbm integration


## Bookmark Manager Integratiaon
- If [twbm · PyPI](https://pypi.org/project/twbm/) is installed `vimania-uri` pushes URI's to the bookmark database with `goo`.
- Pushed bookmarks have default tag `vimania` in the bookmark-manager db.
- Bookmarks are also removed from bookmark-manager database when removed from markdown file with `dd`

### Configuration
```vim
"Plug 'https://github.com/sysid/vimania-uri.git', {'do': 'pip install -r pythonx/requirements.txt --target pythonx'}
  let g:vimania_uri_extensions=['.md','.txt','.rst','.py']
  let g:vimania_uri_twbm_integration=1
```
For bookmark manager [twbm](https://github.com/sysid/twbm) integration the database location needs to be configured:

`export TWBM_DB_URL="sqlite:///$HOME/twbm/todos.db"`




## Installation
- vim needs to be configured with python support
- `pip` must be in path in order to install required dependencies into `vimania/pythonx` (no pollution of system python).

1. Install `https://github.com/sysid/vimania` with your favourite VIM plugin manager
2. Install python `requirements.txt` into `<vimplugins>/vimania-uri/pythonx`

Using [vim-plug](https://github.com/junegunn/vim-plug):

`Plug 'https://github.com/sysid/vimania-uri.git', {'do': 'pip install -r pythonx/requirements.txt --target pythonx'}`


### URIs insertion convenience method:
I recommend configuring [UltiSnips](https://github.com/SirVer/ultisnips) snippets:
```
snippet uri "link/uri for Vimania"
[${1:link}]($1)
endsnippet
```

### Dependencies
- see [requirements.txt](requirements.txt)

Optional:
- [twbm](https://github.com/sysid/twbm) for seamless bookmark manager integration
- [UltiSnips](https://github.com/SirVer/ultisnips) for easy uri and todo creation




# Development
- VIM needs to find vimania dependencies in `pythonx`.
- vim interface cannot be tested within PyCharm, needs to be called from VIM.
- For python changes it is important to restart vim after every change in order to enforce proper reload:
  this is best automated with a Vader script: `run_tests.sh testfile` in tests directory.
- vimscript changes can be reloaded as usual
- `buku.py` needs to be copied from `twbm` package as it is used to push URLs to buku DB.

### Testing
#### Python: pytest
`make test`

#### VIM: Vader
`make test-vim`

#### Smoke Test
- after installation with [Plug](https://github.com/junegunn/vim-plug) run vader tests

### Architecture
![Component](doc/component-vimenia.png)


### Credits
- It is inspired by and recommends to use [UltiSnips](https://github.com/SirVer/ultisnips).
- URI handling is based on work of [mdnav](https://github.com/chmp/mdnav)
- Bookmark management uses [jarun/buku](https://github.com/jarun/buku)


#### Changelog
[CHANGELOG.md](https://github.com/sysid/vimania-uri/blob/master/CHANGELOG.md)

<!-- Badges -->

[pypi-image]: https://badge.fury.io/py/vimania-uri.svg
[pypi-url]: https://pypi.org/project/vimania-uri/
[build-image]: https://github.com/sysid/vimania-uri/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/sysid/vimania-uri/actions/workflows/build.yml
[coverage-image]: https://codecov.io/gh/sysid/vimania-uri/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/sysid/vimania-uri
