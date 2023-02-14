@RD /S /Q dist

pyinstaller ^
	-F --windowed ^
	spriggan-rpc.py

robocopy "./dist/" "./spriggan-client-gui/public/bin/"