.DEFAULT_GOAL := help

MAKE          = make
VERSION       = $(shell cat VERSION)

MAKE    = make
PYTHON	= python
PYTEST	= pytest --log-level=debug --capture=tee-sys --asyncio-mode=auto
PYTOPT	=
VENV	= venv
PIP		= venv/bin/pip

VIM_PLUG="$(HOME)/dev/vim/tw-vim/config/plugins.vim"

app_root = $(PROJ_DIR)/pythonx
app_root ?= .
pkg_src =  $(app_root)/vimania_uri
tests_src = $(app_root)/tests

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z0-9_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("\033[36m%-20s\033[0m %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: all
all: clean build upload tag  ## Build and upload
	@echo "--------------------------------------------------------------------------------"
	@echo "-M- building and distributing"
	@echo "--------------------------------------------------------------------------------"

################################################################################
# Testing
################################################################################
.PHONY: test
test:  ## run tests
	TW_VIMANIA_DB_URL=sqlite:///tests/data/vimania_todos_test.db python -m py.test tests -vv

.PHONY: test-vim
test-vim:  test-vim-uri  ## run tests-vim

.PHONY: test-vim-uri
test-vim-uri:  ## run tests-vim-vimania
	@echo "- > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > - > "
	pushd tests; ./run_test.sh test_vimania_uri.vader; popd
	@echo "- < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < - < "

.PHONY: coverage
coverage:  ## Run tests with coverage
	python -m coverage erase
	TW_VIMANIA_DB_URL=sqlite:///tests/data/vimania_todos_test.db python -m coverage run --include=$(pkg_src)/* --omit=$(pkg_src)/buku.py -m pytest -ra
	#python -m coverage report -m
	python -m coverage html
	python -m coverage report -m
	python -m coverage xml
	#open htmlcov/index.html  # work on macOS

.PHONY: tox
tox:   ## Run tox
	tox

################################################################################
# Building
################################################################################
.PHONY: copy-buku
copy-buku:  ## copy-buku: copy buku.py from twbm
	cp $(HOME)/dev/py/twbm/twbm/buku.py $(pkg_src)/buku.py

#.PHONY: build
#build: clean-vim ## build
#	@echo "building"
#	#python setup.py sdist
#	cp README.md pythonx/
#	pushd pythonx; python -m build; popd

#.PHONY: build-vim-dev
#build-vim-dev: _confirm ## copy all python packages into pythonx (for local installation)
#	./scripts/cp_venv.sh dev
#	cp -a ~/dev/py/pure-sql/src/pure_sql ~/dev/vim/vimania/pythonx

.PHONY: build-vim
build-vim: _confirm clean-vim ## clean and re-install via pip into pythonx
	pip install -r pythonx/requirements.txt --target pythonx

.PHONY: clean-vim
clean-vim:  ## clean pythonx directory for PyCharm development
	@echo "Removing python packages from pythonx"
	@pushd pythonx; git clean -d -x -f; popd


.PHONY: requirements
requirements:  ## create requirements.txt
	#pipenv lock -r > pythonx/requirements.txt
	vim pythonx/requirements.txt

.PHONY: vim-install
vim-install:  ## vim Plug install
	sed -i.bkp "s#^\"Plug 'https://github.com/sysid/vimania-uri.git'#Plug 'https://github.com/sysid/vimania-uri.git'#" $(VIM_PLUG)
	sed -i.bkp "s#^Plug '~/dev/vim/vimania-uri'#\"Plug '~/dev/vim/vimania-uri'#" $(VIM_PLUG)
	vim -c ':PlugInstall vimania-uri'

.PHONY: vim-uninstall
vim-uninstall:  ## vim Plug uninstall
	[ -d "$(HOME)/.vim/plugged/vimania-uri" ] && rm -fr "$(HOME)/.vim/plugged/vimania-uri"
	sed -i.bkp "s#^\"Plug '~/dev/vim/vimania-uri'#Plug '~/dev/vim/vimania-uri'#" $(VIM_PLUG)
	sed -i.bkp "s#^Plug 'https://github.com/sysid/vimania-uri.git'#\"Plug 'https://github.com/sysid/vimania-uri.git'#" $(VIM_PLUG)


################################################################################
# Version, Uploading
################################################################################
.PHONY: upload
upload:  ## upload to PyPi
	@echo "upload"
	twine upload --verbose pythonx/dist/*

.PHONY: tag
tag:  ## tag with VERSION
	@echo "tagging $(VERSION)"
	git tag -a $(VERSION) -m "version $(VERSION)"
	git push --tags

.PHONY: bump-major
bump-major:  ## bump-major
	bumpversion --verbose major

.PHONY: bump-minor
bump-minor:  ## bump-minor
	bumpversion --verbose minor

.PHONY: bump-patch
bump-patch:  ## bump-patch
	#bumpversion --dry-run --allow-dirty --verbose patch
	bumpversion --verbose patch


################################################################################
# Code Quality
################################################################################
.PHONY: style
style: isort format  ## perform code style format (black, isort)

.PHONY: format
format:  ## perform black formatting
	black --exclude="buku.py" $(pkg_src) tests

.PHONY: isort
isort:  ## apply import sort ordering
	isort $(pkg_src) --profile black

.PHONY: lint
lint: flake8 mypy ## lint code with all static code checks

.PHONY: flake8
flake8:  ## check style with flake8
	@flake8 $(pkg_src)

.PHONY: mypy
mypy:  ## check type hint annotations
	# keep config in setup.cfg for integration with PyCharm
	mypy --config-file setup.cfg $(pkg_src)

################################################################################
# Clean
################################################################################
.PHONY: clean
clean: clean-build clean-pyc  ## remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr pythonx/build/
	rm -fr pythonx/dist/
	rm -fr pythonx/.eggs/
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg-info' -exec rm -fr {} +
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

################################################################################
# Misc
################################################################################
.PHONY: dev
dev: _confirm clean-vim  ## develop python module, prep accordingly
	pycharm .

.PHONY: dev-vim
dev-vim:  ## open vim plugin
	vim -c 'OpenSession vimania-uri'

.PHONY: _confirm
_confirm:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo "Action confirmed by user."
