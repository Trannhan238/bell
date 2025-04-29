@echo off
:menu
cls
echo ================================
echo      GIT SYNC TOOL 
echo ================================
echo.
echo Chon tac vu:
echo [D] Download (git pull)
echo [U] Upload (git push)
echo [Q] Thoat
echo.
set /p choice=Nhap lua chon (D/U/Q): 

if /i "%choice%"=="D" goto download
if /i "%choice%"=="U" goto upload
if /i "%choice%"=="Q" exit
goto menu

:download
echo.
set /p confirm=Ban co chac muon DOWNLOAD code ve? (y/n): 
if /i "%confirm%"=="Y" (
    echo Dang download...
    git fetch origin
    git reset --hard origin/main
    echo Download hoan thanh!
) else (
    echo Huy download.
)
pause
goto menu

:upload
echo.
set /p confirm=Ban co chac muon UPLOAD code len? (y/n): 
if /i "%confirm%"=="Y" (
    echo Dang upload...
    git add .
    git commit -m "Auto commit at %date% %time%"
    git push origin main --force
    echo Upload hoan thanh!
) else (
    echo Huy upload.
)
pause
goto menu
