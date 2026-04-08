@echo off
REM Build the React Task Pane for production
echo Building Task Pane...
cd taskpane
call npm install
call npm run build
echo Output: taskpane\dist\
cd ..
pause
