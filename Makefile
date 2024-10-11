PYTHON = python3

build:
	$(PYTHON) -m build -n

install: build
	$(PYTHON) -m pip install --user --force-reinstall --break-system-packages dist/panmuphle-*-py3-none-any.whl
