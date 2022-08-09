# Vimania

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]

> Vimania is a modern and extensible set of functions to be used with VIM and markdown files.

Key features:

1. Handler for arbitrary URIs in markdown files
2. Automated todo management with database backend. Todos are synchronized between markdown source file and database,
   i.e. todos can be updated direct in the DB.
3. It integrates seamless with bookmark manager [twbm](https://github.com/sysid/twbm).

## 1. Handler for URIs

It provides its versatility via a super simple user interface:

    go (go open: URL, directories, files, ...)
    goo (go open and save to DB, requires twbm)
    dd (delete from text and DB)

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

Inside normal model with an open markdown document, you may press `go` on a
markdown link to open it.
If the link is a local file it will be opened in vim (`C-o` will get you back),
otherwise it will be opened by the current webbrowser.

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

- `g:vimania#Extensions`:
    a comma separated list of file extensions.
    Only file s with the given extensions will be opened in vim, all other
    files will be opened via the configured application (using `open` on OSX
    and `xdg-open` on linux).
    This option may be useful to link to non-text documents, say PDF files.


## 2. Automated Todo/Task list management

- Centralized todo list management with embedded database, keep your todo items within the context/file where they
  belong but have a centralized view on it
- no more missing, obsolete or duplicated todos
- Synchronization of todo status between Markdown files and database
- todo lists within code fences in markdown are ignored
- DB entry has a link to the task's source file, so by looking in the DB any todo can be located.
- Todos are removed from database when removed from markdown file with `dd`

### CLI interface
- `vimania` provides a CLI interface with full-text search capabilities to your todo database:

```bash
vimania -h

vimania search
```

The CLI interface is identical to the `twbm` CLI interface.

### URL management: `twbm` integration

- If `twbm` is installed `Vimania` pushes URL's to the bookmark database transparently when opening the bookmark
  with `goo`.
- Pushed bookmarks have the default tag `vimania` in the bookmarks db.
- Bookmarks are removed from bookmarks database when removed from markdown file with `dd`

### Insert URIs and Todos convenience method:

I recommend configuring two [UltiSnips](https://github.com/SirVer/ultisnips) snippets:

```
snippet todo "todo for Vimania"
- [ ] ${1:todo}
endsnippet

snippet uri "link/uri for Vimania"
[${1:link}]($1)
endsnippet
```

## Installation
- vim needs to be configured with python support.
- `pip` must be in path in order to install required dependencies into `vimania/pythonx` (no pollution of system python).

1. Install `https://github.com/sysid/vimania` with your favourite VIM plugin manager
2. Install python `requirements.txt` into `<vimplugins>/vimania/pythonx`
3. Install CLI interface: `make install` (requires pipx)

Example:  
`Plug 'https://github.com/sysid/vimania.git', {'do': 'pip install -r pythonx/requirements.txt --target pythonx'}`



### Dependency
Currently [vim-textobj-uri](https://github.com/jceb/vim-textobj-uri) must be installed for URI identification.
This is going to change soon.

Optional:
[twbm](https://github.com/sysid/twbm) for seamless bookmark manager integration
[UltiSnips](https://github.com/SirVer/ultisnips) for easy uri and todo creation


### Configuration

Vimenia needs to know, where your Todos database is located:
`TW_VIMANIA_DB_URL="sqlite:///$HOME/vimania/todos.db"`

Optionally where your twbm database is located:
`TWBM_DB_URL="sqlite:///$HOME/twbm/todos.db"`


# Implementation Details
## Architecture
![Component](doc/component-vimenia.png)

## Todo Management

- Todos are recognized via the format: `- [ ] todo`
- On opening Vimania scans the markdown files and updates existing todos with the current state from the database
- On saving Vimania scans the markdown and saves new or updated todos to the database
- Vimania inserts a DB identifier ('%99%') into the markdown item in order to establish a durable link between DB and
  markdown item
- The identifier is hidden via VIM's `conceal` feature
- todo items are deleted by deleting (`dd`) in normal mode. This triggers a DB update
- todo items deleted by `dd` in visual mode are NOT delete from DB. This is useful to move tasks from one file to
  another. Otherwise, you always can move an item by just deleting it in one file and paste in to another file AND then
  remove the database id ('%99%'). So Vimania kust creates a new entry/link.

### Example todo file

After saving the file, the identifiers have been added and the items are saved in DB:

```markdown
-%1% [ ] purchase piano -%2% [ ] [AIMMS book](file:~/dev/pyomo/tutorial/AIMMS_modeling.pdf)
-%7% [ ] list repos ahead/behind remote
```

## Caveat

- Deleting markdown todo items outside Vimenia will cause inconsistency between the DB and the markdown state.
- Always use `dd` to delete a markdown item in order to trigger the corresponding DB update
- Never change the identifier '%99%' manually.
- Todo items are always synced from the DB when opening a markdown file, so changes not written back to DB will be
  lost.

Markdown content other than todo items can be changed arbitrarily, of course.

### Fixing inconsistent state

Todos in markdown can get out of sync if updates are made outside of vim, e.g. with another text editor. Don't worry,
this can be fixed easily.

#### entry already in DB

- find the corresponding id in the DB
- add the id to the markdown item: `-%99% [ ] markdown item`

### entry in DB but not in markdown

- you can safely delete the entry in the DB, unless you maintain on purpose todo items in the DB which do not have a
  counterpart in a markdown (I do).

#### Resetting everything

Deleting/adding todo items outside the control of Vimania can cause an inconsistent state between the database on the
markdown files. It is possible to re-synchronize the DB and the todo-lists by creating a new database and clearing the
todo items fo their identifier:

1. Reset DB: `cd pythonx/vimania/db; rm todos.db; alembic upgrade head`
2. Clean up existing markdown files:
    - find all affected markdown files: `rg -t md -- '-%\d+%'`
    - edit the markdown files and remove the allocated database-id to allow for
      re-init: `sed -i 's/-%[0-9]\+%/-/' todo.md`


# Development
VIM needs to find vimania dependencies in `pythonx`.
However, try to avoid bringing up PyCharm because it tries to index the entire dependency tree.

## VimaniaManager (VIM Interface)
- cannot be tested within PyCharm, needs to be called from VIM.

## Python only
PyCharm's source directory should be `pythonx`.
So before starting PyCharm run `make clean-vim` to clear `pythonx`.
Deps will be found in `.venv`.

## Other
- `buku.py` needs to be copied from `twbm` package as it is used to push URLs to buku DB.


## Testing
- deactivate autocommand `:Vista` if active

Setup: Make sure that the working directory of test-runs is the project-root (e.g. in PyCharm)
`make test`
`make test-vim`

### VIM bridge

- For python changes it is important to restart vim after every change in order to enforce proper reload:
  this is best automated with a Vader script: `run_tests.sh testfile` in tests directory.
- vimscript changes can be reloaded as usual

### textobj/uri

- Use vim mapping `go` on the `*.vader` URIs. -- Regexp: https://regex101.com/r/LpSX0i/1

### Example

Example for registration of additional object and their handler:

```vim
" location: after/plugin/textobj_uri.vim
if ! exists('g:loaded_uri')
  echom "-W- vim-textobj-uri not availabe, please install."
  finish
endif

if g:twvim_debug | echom "-D- vim-textobj-uri is installed, registering patterns." | endif
" example pattern
URIPatternAdd! vimania://\%(\([^()]\+\)\) :silent\ !open\ "%s"
```

# TODO

todo status enum: [enum](https://stackoverflow.com/questions/5299267/how-to-create-enum-type-in-sqlite)
todos link check from DB

- resilience against external deleting
- hierarchical todos
- use yes/no interaction with vim

### Manual todo testing

reset db: `alembic upgrade head`

# Credits

It is inspired by and recommends to use [UltiSnips](https://github.com/SirVer/ultisnips).
URI handling is based on [mdnav](https://github.com/chmp/mdnav)


## Changelog
[CHANGELOG.md](https://github.com/sysid/vimania/blob/master/CHANGELOG.md)

<!-- Badges -->

[pypi-image]: https://badge.fury.io/py/vimania.svg
[pypi-url]: https://pypi.org/project/vimania/
[build-image]: https://github.com/sysid/vimania/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/sysid/vimania/actions/workflows/build.yml
[coverage-image]: https://codecov.io/gh/sysid/vimania/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/sysid/vimania
