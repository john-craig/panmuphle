PYTHON = python3.12

build:
	$(PYTHON) -m build

install: build
	$(PYTHON) -m pip install --user --break-system-packages --force-reinstall dist/panmuphle-*-py3-none-any.whl
