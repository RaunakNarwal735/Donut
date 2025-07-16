@echo off
:: Set your project directory
cd "C:\Users\rishu narwal\Desktop\Donut"

:: Add all changes (modified, new, deleted files)
git add .

:: Check if there are changes (skip empty commits)
git diff-index --quiet HEAD
IF %ERRORLEVEL% EQU 0 (
    echo No changes detected. No commit created.
) ELSE (
    git commit -m "Auto-commit %date% %time%"
    git push origin main
    echo Changes committed and pushed.
)

pause
