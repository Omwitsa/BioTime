#!python26.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pypm==0.2.0b2.dev-r1117','console_scripts','pypm-repository'
__requires__ = 'pypm==0.2.0b2.dev-r1117'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('pypm==0.2.0b2.dev-r1117', 'console_scripts', 'pypm-repository')()
    )
