@echo off
setlocal

pushd %~dp0

if not defined GAE_ROOT set GAE_ROOT=..

python %GAE_ROOT%\appcfg.py update .

popd
