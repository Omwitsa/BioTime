#!python.exe
import site

# $Id: exemaker.py 289 2004-10-11 22:32:18Z fredrik $
# install the given script in the given target directory

import sys, os, getopt

VERSION = "1.2/2004-10-12"

def usage():
    print "ExeMaker", VERSION, "(c) 2004 by Fredrik Lundh."
    print
    print "Usage:"
    print
    print "    exemaker [-i interpreter] scriptname [target-dir]"
    print
    print "installs the given script in the target directory, and creates"
    print "an EXE file in the same directory, that runs the script."
    print
    print "If the target directory is omitted, it defaults to the exemaker"
    print "installation directory (%s)" % target
    print
    print "Options:"
    print
    print "  -i file   Interpreter DLL or EXE (default is %s)." % interpreter
    print
    print "For more information on ExeMaker, see",
    print "http://effbot.org/zone/exemaker.htm"
    print
    print "(Using Python", sys.version.split()[0] + ")"
    sys.exit(1)

target = os.path.dirname(sys.executable)

interpreter = "python%s%s.dll" % (sys.version[0], sys.version[2])
interpreter = "python.exe" # use the binary, for now

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:")
except getopt.error:
    usage()

if not args:
    usage()

scriptfile = args[0]

if len(args) > 2:
    usage()

if len(args) > 1:
    target = args[1]

for k, v in opts:
    if k == "-i":
        interpreter = v

# figure out what to install, and where to install it

loader = sys.executable

scriptbase, ext = os.path.splitext(os.path.basename(scriptfile))
if not ext:
    scriptfile = scriptfile + ".py"

loader_source = sys.executable
loader_target = os.path.join(target, scriptbase + ".exe")

if os.path.abspath(loader_source) == os.path.abspath(loader_target):
    print "Cannot overwrite myself.  Please specify a target directory."
    sys.exit(1)

script_source = scriptfile
script_target = os.path.join(target, scriptbase + ".py")

def copy(source, target, prefix=None):
    data = open(source, "rb").read()
    file = open(target, "wb")
    if prefix:
        file.write(prefix)
    file.write(data)
    file.close()
    print os.path.normpath(target), "ok"

copy(loader_source, loader_target)
copy(script_source, script_target, "#!%s\nimport site\n\n" % interpreter)
