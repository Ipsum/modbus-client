@echo off
echo Change version numbers in setup.py and installer-options.txt
pause
rem set CLARK_ROOT="C:\Program Files\Mercurial"
set CLARK_ROOT="D:\_Clark"
set AI_DIR="C:\Tools\Caphyon\Advanced Installer 8.5\bin\x86"
chdir /d %CLARK_ROOT%\modbus-client-future\
rem cd "D:\_Clark\modbus-client-future\"
python setup.py install
python -OO setup.py py2exe
".\Automated Build\UPX\upx.exe" ".\dist\Microsoft.VC90.CRT\msvcr90.dll" ".\dist\_ctypes.pyd" ".\dist\_socket.pyd" ".\dist\_tkinter.pyd" ".\dist\bz2.pyd" ".\dist\Commissioning.exe" ".\dist\python27.dll" ".\dist\tcl85.dll" ".\dist\tk85.dll" ".\dist\w9xpopen.exe" ".\dist\unicodedata.pyd"
echo. Do manual cleanup
pause
%AI_DIR%\AdvancedInstaller.com /execute ".\Automated Build\Installer Config.aip" ".\Automated Build\installer-options.txt"
echo Deleting build output directory
rmdir build\ /s /q
pause
echo Deleting distribution directory
rmdir dist\ /s /q