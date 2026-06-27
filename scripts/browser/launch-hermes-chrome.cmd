@echo off
setlocal
set "CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "PROFILE=C:\Users\Ryan\AppData\Local\hermes\browser-profiles\cdp-chrome"
set "SPLASH=file:///C:/Users/Ryan/gig-factory/docs/continuity/hermes-browser-start.html"
if not exist "%CHROME%" (
  echo Chrome not found at %CHROME%
  exit /b 1
)
if not exist "%PROFILE%" mkdir "%PROFILE%"
start "Hermes Controlled Chrome" "%CHROME%" --remote-debugging-port=9222 --user-data-dir="%PROFILE%" --new-window "%SPLASH%" "https://github.com/login"
exit /b 0
