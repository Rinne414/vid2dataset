@echo off
chcp 65001 >nul
title vid2dataset
cd /d "%~dp0"

echo.
echo   ==========================================
echo    vid2dataset
echo    Double-click to start  /  双击启动
echo   ==========================================
echo.

if exist "%~dp0vid2dataset.exe" (
    echo Starting vid2dataset.exe ...
    echo 正在启动 vid2dataset.exe ...
    start "" "%~dp0vid2dataset.exe"
    exit /b 0
)

if exist "%~dp0dist\vid2dataset.exe" (
    echo Starting dist\vid2dataset.exe ...
    echo 正在启动 dist\vid2dataset.exe ...
    start "" "%~dp0dist\vid2dataset.exe"
    exit /b 0
)

set "PYW="
if exist "%~dp0venv\Scripts\pythonw.exe" set "PYW=%~dp0venv\Scripts\pythonw.exe"
if exist "%~dp0.venv\Scripts\pythonw.exe" set "PYW=%~dp0.venv\Scripts\pythonw.exe"

if defined PYW (
    echo Starting from local Python environment ...
    echo 正在从本机 Python 环境启动 ...
    start "" "%PYW%" -m vid2dataset app
    exit /b 0
)

echo.
echo  [Cannot start yet / 还不能启动]
echo.
echo  Do ONE of these:
echo  请任选一种方式：
echo.
echo   1. Download vid2dataset.exe from GitHub Releases
echo      and put it in this folder, then double-click START.bat again.
echo      从 GitHub Releases 下载 vid2dataset.exe 放到本文件夹，再双击 START.bat。
echo.
echo   2. Double-click  install.bat  once, then double-click START.bat.
echo      先双击 install.bat 安装一次，再双击 START.bat。
echo.
echo   Releases:
echo   https://github.com/Rinne414/vid2dataset/releases
echo.
pause
exit /b 1
