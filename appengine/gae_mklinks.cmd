@echo off
setlocal

pushd %~dp0\lib

FOR %%p IN (chardet cssselect readability codepen) DO (
  IF EXIST "%%p" (
    echo Existing lib: %%p
  ) ELSE (
    echo|set /p="Linking: %%p ... "
    mklink /d %%p ..\..\%%p
  )
)
