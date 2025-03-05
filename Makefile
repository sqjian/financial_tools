all: run

run:
	uv run ui.py

pack:
	uv run pyinstaller \
		--onefile \
		--icon=res/doraemon.ico \
		--noconsole \
		--name="doraemon.exe" \
		ui.py