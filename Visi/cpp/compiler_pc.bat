@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Compilation de la DLL pour le PC...
g++ -shared -O2 -static -Dcimg_display=0 -o ..\marque.dll pont.cpp -lgdi32
if errorlevel 1 (echo ECHEC de la compilation & pause & exit /b 1)
echo OK : marque.dll créée. Relance lancer.bat.
pause
