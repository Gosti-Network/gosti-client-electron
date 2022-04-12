@RD /S /Q dist


%PYTHONPATH%\Scripts\\pyinstaller.exe ^
	-F --windowed --"icon=img/SPRIGGAN.ico" ^
	main.py

cd dist

7z a SPRIGGAN_v%1.zip *

cd ..

del spriggan.wixobj
del spriggan.wixpdb

move spriggan.msi dist/SPRIGGAN_v%1.msi
