all: clean dev

run:
	uv run main.py

dev:
	uv run dev.py

clean:
	cls
pack:
	uv run pyinstaller \
		--onefile \
		--icon=res/doraemon.ico \
		--noconsole \
		--name="doraemon.exe" \
		main.py