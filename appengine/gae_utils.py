import os
import os.path as path
from sys import stdout, stderr, exit

LIBS = [
    'chardet',
    'cssselect',
    'readability',
    'static',
]

try:
    from os import symlink
except ImportError: # windows :(
    def symlink(source, link_name):
        from subprocess import call
        call(['cmd.exe', '/c', 'mklink', '/d', link_name, source])


def _gae_mklinks(lib_names):
    orig_dir  = os.getcwd()
    file_dir  = path.split(__file__)[0]
    lib_links = 'lib'

    os.chdir(file_dir)

    if not path.exists(lib_links):
        os.mkdir(lib_links)

    os.chdir(lib_links)

    lib_target = path.abspath(path.join(file_dir, '..'))

    for lib in lib_names:
        if path.exists(lib):
            stdout.write('Existing lib: %s\n' % lib)
        else:
            stdout.write('Linking: %s ... ' % lib)
            full_lib_path = path.join(lib_target, lib)
            if not path.exists(full_lib_path):
                stderr.write('\nERROR: %s not found!\n' % full_lib_path)
                exit(-1)

            symlink(full_lib_path, lib)

    os.chdir(orig_dir)

def gae_mklinks():
    _gae_mklinks(LIBS)

def gae_exec_tool(tool, args=''):
    orig_dir = os.getcwd()
    file_dir = path.split(__file__)[0]
    gae_root = os.environ.get('GAE_ROOT', '..')

    os.chdir(file_dir)

    script = tool + '.py'
    script = os.path.join(gae_root, script)

    if not path.exists(script):
        stderr.write('ERROR: %s not found!\n' % script)
        exit(-1)

    try:
        # Feeding bare 'python' to shell should take care of virtualenv
        os.system('python {} {}'.format(script, args))
    except KeyboardInterrupt:
        pass

    os.chdir(orig_dir)

