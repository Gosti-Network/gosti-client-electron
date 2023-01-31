@RD /S /Q dist

pyinstaller ^
	-F --windowed ^
	spriggan-rpc.py

@REM robocopy "dist/spriggan-rpc.exe" "SprigganGui/dist/spriggan-rpc.exe"