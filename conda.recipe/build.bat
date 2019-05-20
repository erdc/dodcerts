@REM Build

python setup.py install --single-version-externally-managed --record=record.txt

goto end
@REM Add activate/deactivate scripts

set ACTIVATE_DIR=%PREFIX%\etc\conda\activate.d
set DEACTIVATE_DIR=%PREFIX%\etc\conda\deactivate.d
mkdir %ACTIVATE_DIR%
mkdir %DEACTIVATE_DIR%

copy %RECIPE_DIR%\scripts\activate.bat %ACTIVATE_DIR%\dodcerts-activate.bat
if errorlevel 1 exit 1

copy %RECIPE_DIR%\scripts\deactivate.bat %DEACTIVATE_DIR%\dodcerts-deactivate.bat
if errorlevel 1 exit 1

@REM Copy unix shell activation scripts, needed by Windows Bash users

copy %RECIPE_DIR%\scripts\activate.sh %ACTIVATE_DIR%\dodcerts-activate.sh
if errorlevel 1 exit 1

copy %RECIPE_DIR%\scripts\deactivate.sh %DEACTIVATE_DIR%\dodcerts-deactivate.sh
if errorlevel 1 exit 1

:end
