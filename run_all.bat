@echo off
setlocal enabledelayedexpansion

@REM TODO: check removed index (toc) from docx.

set EXT=docx

set FOLDER=%DATE:~9,4%-%DATE:~6,2%-%DATE:~3,2%
echo --------------------
echo %FOLDER%

if not exist %FOLDER% (
    mkdir %FOLDER%
)

set ZIPFILE=%FOLDER%\db.zip
echo Download alle data van de database...

if not exist %ZIPFILE% (
    python app.py db.yaml %ZIPFILE% || exit /b 1
    echo Download klaar.
) else (
    echo %ZIPFILE% bestaat al.
)

echo Exporteer alle stadsdelen...
echo === BEWONERS ===

for %%s in (Centrum Nieuw-West Noord Oost Weesp West Zuid Zuidoost) do (
    set "OUTFILE=%FOLDER%\Afvalwijzer %%s - bewoners.%EXT%"
    echo !OUTFILE!
    python app.py %ZIPFILE% "!OUTFILE!" --stadsdeel %%s --bewoners
)

echo === BEDRIJVEN ===

for %%s in (Centrum Nieuw-West Noord Oost Weesp West Zuid Zuidoost) do (
    set "OUTFILE=%FOLDER%\Afvalwijzer %%s - bedrijven.%EXT%"
    echo !OUTFILE!
    python app.py %ZIPFILE% "!OUTFILE!" --stadsdeel %%s --bedrijven
)

echo ---
echo Klaar.
