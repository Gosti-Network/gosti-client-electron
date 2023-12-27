@RD /S /Q dist

pyinstaller -F --windowed --add-data="../../chia-blockchain/chia/wallet/puzzles/*;chia/wallet/puzzles/" --add-data="../../chia-blockchain/chia/wallet/util/*;chia/wallet/util/" gosti-rpc.py

robocopy "./dist/" "./gosti-client-gui/"
cp "./gosti-config-dist.json" "./gosti-client-gui//gosti-config.json"