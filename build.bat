@RD /S /Q dist

pyinstaller -F --windowed --add-data="../../chia-blockchain/chia/wallet/puzzles/*;chia/wallet/puzzles/" --add-data="../../chia-blockchain/chia/wallet/util/*;chia/wallet/util/" spriggan-rpc.py

robocopy "./dist/" "./spriggan-client-gui/"
cp "./spriggan-config-dist.json" "./spriggan-client-gui//spriggan-config.json"