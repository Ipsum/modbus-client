@echo off
echo Change version numbers in setup.py and installer-options.txt
pause
cd "C:\Program Files\Mercurial\modbus-client\"
python setup.py install
python -OO setup.py py2exe
"C:\Program Files\Mercurial\modbus-client\Automated Build\UPX\upx.exe" --brute "C:\Program Files\Mercurial\modbus-client\dist\Microsoft.VC90.CRT\msvcr90.dll" "C:\Program Files\Mercurial\modbus-client\dist\_ctypes.pyd" "C:\Program Files\Mercurial\modbus-client\dist\_hashlib.pyd" "C:\Program Files\Mercurial\modbus-client\dist\_socket.pyd" "C:\Program Files\Mercurial\modbus-client\dist\_tkinter.pyd" "C:\Program Files\Mercurial\modbus-client\dist\bz2.pyd" "C:\Program Files\Mercurial\modbus-client\dist\Comissioning.exe" "C:\Program Files\Mercurial\modbus-client\dist\python27.dll" "C:\Program Files\Mercurial\modbus-client\dist\tcl85.dll" C:\Program Files\Mercurial\modbus-client\dist\tk85.dll" "C:\Program Files\Mercurial\modbus-client\dist\w9xpopen.exe" "C:\Program Files\Mercurial\modbus-client\dist\unicodedata.pyd"
"C:\Program Files\Caphyon\Advanced Installer 8.5\bin\x86\AdvancedInstaller.com" /execute "C:\Program Files\Mercurial\modbus-client\Automated Build\Installer Config.aip" "C:\Program Files\Mercurial\modbus-client\Automated Build\installer-options.txt"
rmdir build\ /s /q
pause