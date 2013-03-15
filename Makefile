
LIBS_DIR='libs/'


install_deps:
	pip install --ignore-installed --target=${LIBS_DIR} -r requirements.txt

deploy: install_deps
	appcfg.py update .

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +

clean: clean-pyc
	-rm -fr libs/*

.PHONY: libs deploy clean clean-pyc
