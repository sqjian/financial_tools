all: clean run

run:
	uv run main.py

clean:
	clear

pack:
	uv run pyinstaller \
		--onefile \
		--icon=res/doraemon.ico \
		--noconsole \
		--name="doraemon.exe" \
		main.py