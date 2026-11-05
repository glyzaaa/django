@echo off
call "%~dp0START.bat" --lan %*
exit /b %ERRORLEVEL%
