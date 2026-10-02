@echo off
TITLE Install AgentZ Auto-Start on Windows Boot
echo =======================================================================
echo          AgentZ — Configure Automatic Startup on Windows Boot
echo =======================================================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TARGET_BAT=%~dp0run_laptop_agent.bat"
set "VBS_SCRIPT=%TEMP%\create_agentz_shortcut.vbs"

echo Creating background startup shortcut in:
echo %STARTUP_FOLDER%
echo.

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%STARTUP_FOLDER%\AgentZ_Background.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%TARGET_BAT%" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%~dp0" >> "%VBS_SCRIPT%"
echo oLink.WindowStyle = 7 >> "%VBS_SCRIPT%"
echo oLink.Description = "AgentZ 24/7 Background Service" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

cscript //nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

echo [SUCCESS] AgentZ will now automatically launch in the background whenever your PC boots!
echo.
pause
