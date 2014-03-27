@echo off
setlocal

pushd %~dp0

call gae_mklinks.cmd

if not defined GAE_ROOT set GAE_ROOT=..

python %GAE_ROOT%\dev_appserver.py .

popd
