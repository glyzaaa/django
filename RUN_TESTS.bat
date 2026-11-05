@echo off
call "%~dp0scripts\launch.bat" tests
exit /b %ERRORLEVEL%
