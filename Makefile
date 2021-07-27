#
#   MIT Licensed
#
#   git@github.com/rstms/mvdcim
#   mkrueger@rstms.net
#

PROJECT=$(notdir $(shell pwd))

help:
	@echo Project: $(PROJECT)
	@echo Targets: $$(awk -F: '/^[[:graph:]]*:/{print $$1}' Makefile)

install-test:
	sudo pip3 install -U -e .[test]

install:
	sudo pip3 install -U -e .

uninstall:
	sudo pip3 uninstall mvdcim

test: install
	dotenv run pytest

debug:
	dotenv run pytest --pdb

bump-patch:
	bumpversion patch

bump-minor:
	bumpversion minor

bump-major:
	bumpversion major
