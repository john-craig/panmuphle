PYTHON = python3

build:
	$(PYTHON) -m build -n

install: build
	$(PYTHON) -m pip install --user --force-reinstall --no-deps --break-system-packages dist/panmuphle-*-py3-none-any.whl
