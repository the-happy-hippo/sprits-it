@echo off
setlocal

set LIB_LINKS=%~dp0\lib

if NOT EXIST "%LIB_LINKS%" md "%LIB_LINKS%"

pushd "%LIB_LINKS%\..\.."

set LIB_TARGET=%CD%

cd "%LIB_LINKS%"

FOR %%p IN (chardet cssselect readability static) DO (
  IF EXIST "%%p" (
    echo Existing lib: %%p
  ) ELSE (
    echo|set /p="Linking: %%p ... "
    mklink /d %%p "%LIB_TARGET%\%%p"
  )
)

