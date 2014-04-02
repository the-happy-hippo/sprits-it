from gae_utils import gae_mklinks, gae_exec_tool

gae_mklinks()
gae_exec_tool('dev_appserver', '.')
