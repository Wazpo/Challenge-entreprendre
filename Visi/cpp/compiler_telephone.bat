@echo off
chcp 65001 >nul
cd /d "%~dp0"
where em++ >nul 2>nul || call C:\emsdk\emsdk_env.bat >nul
echo Compilation en WebAssembly pour le telephone...
call em++ pont.cpp -O2 -Dcimg_display=0 -o ..\static\marque.js -sMODULARIZE -sEXPORT_NAME=ModuleMarque -sALLOW_MEMORY_GROWTH -sEXPORTED_FUNCTIONS=_marquer,_malloc,_free -sEXPORTED_RUNTIME_METHODS=HEAPU8
if errorlevel 1 (echo ECHEC de la compilation & pause & exit /b 1)
echo OK : static\marque.js et static\marque.wasm crees. Recharge la page sur le telephone.
pause
