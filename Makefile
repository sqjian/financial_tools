all: dev

run:
	uv run main.py

dev:
	uv run dev.py

pack:
	uv run pyinstaller \
		--onefile \
		--icon=res/doraemon.ico \
		--noconsole \
		--name="doraemon.exe" \
		main.py