@RD /S /Q dist


%PYTHONPATH%\Scripts\\pyinstaller.exe ^
	-F --windowed --"icon=img/DACT.ico" ^
	dact.py

cd dist

7z a DACT_v%1.zip *

cd ..

candle.exe dact.wxs
light.exe dact.wixobj

del dact.wixobj
del dact.wixpdb

move dact.msi dist/DACT_v%1.msi
