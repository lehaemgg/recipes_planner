@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Building executable...
pyinstaller build.spec

echo Done! FoodPlanner.exe is in the dist folder
pause