#!python26.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'virtualenv==1.4.5','console_scripts','virtualenv'
__requires__ = 'virtualenv==1.4.5'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('virtualenv==1.4.5', 'console_scripts', 'virtualenv')()
    )
