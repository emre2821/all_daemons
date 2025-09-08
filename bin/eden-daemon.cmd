@echo off
setlocal EnableExtensions EnableDelayedExpansion
set PY=%~dp0\..\Daemon_tools\scripts\eden_daemon.py
if not defined EDEN_ROOT set EDEN_ROOT=%cd%\..
python "%PY%" %*

