#!/usr/bin/python

"""
replacement for runtest target in Makefile
"""

from __future__ import print_function
from argparse import ArgumentParser, RawTextHelpFormatter
import os
import os.path
import platform
import subprocess
import sys
import time

winsfx = ".exe"
testsfx = "_test.cpp"


def processCLIArgs():
    """
    Define and process the command line interface to the runTests.py script.
    """
    cli_description = "Generate and run Stan tests."
    cli_epilog = "See more information at: https://github.com/stan-dev/stan"

    parser = ArgumentParser(description=cli_description,
                            epilog=cli_epilog,
                            formatter_class=RawTextHelpFormatter)

    # Now define all the rules of the command line args and opts
    parser.add_argument("-j", metavar="N", type=int, default=1,
                        help="number of cores for make to use")

    tests_help_msg = "The path(s) to the test case(s) to run.\n"
    tests_help_msg += "Example: 'src/test/unit', 'src/test/integration', and/or\n"
    tests_help_msg += "         'src/test/unit/util_test.cpp'"
    parser.add_argument("tests", nargs="+", type=str,
                        help=tests_help_msg)
    # parser.add_argument("-m", "--make-only", dest="make_only",
    #                     action="store_true", help="Don't run tests, just try to make them.")

    # And parse the command line against those rules
    return parser.parse_args()

def stopErr(msg, returncode):
    """Report an error message to stderr and exit with a given code."""
    sys.stderr.write('%s\n' % msg)
    sys.stderr.write('exit now (%s)\n' % time.strftime('%x %X %Z'))
    sys.exit(returncode)

def doCommand(command, exit_on_failure=True):
    """Run command as a shell command and report/exit on errors."""
    print("------------------------------------------------------------")
    print("%s" % command)
    p1 = subprocess.Popen(command, shell=True)
    p1.wait()
    if exit_on_failure and (not(p1.returncode is None) and not(p1.returncode == 0)):
        stopErr('%s failed' % command, p1.returncode)

def isWin():
    return (platform.system().lower().startswith("windows")
            or os.name.lower().startswith("windows"))

# set up good makefile target name
def mungeName(name):
    if (name.startswith("src") or name.startswith("./src")):
        name = name.replace("src/","",1)
    if (name.endswith(testsfx)):
        name = name.replace(testsfx,"_test")
        if (isWin()):
            name += winsfx
            name = name.replace("\\\\","/")
            name = name.replace("\\","/")
    return name

def makeMathLibs(j):
    if isWin():
        doCommand('mingw32-make -j%d -f lib/stan_math/make/standalone math-libs' % j)
    else:
        doCommand('make -j%d -f lib/stan_math/make/standalone math-libs' % j)

def findTests(base_path):
    folders = filter(os.path.isdir, base_path)
    nonfolders = list(set(base_path) - set(folders))
    tests = nonfolders + [os.path.join(root, n)
            for f in folders
            for root, _, names in os.walk(f)
            for n in names
            if n.endswith(testsfx)]
    tests = map(mungeName, tests)
    return tests


def makeTest(name, j):
    """Run the make command for a given single test."""
    if isWin():
        doCommand('mingw32-make -j%d %s' % (j or 1, name))
    else:
        doCommand('make -j%d %s' % (j or 1, name))

def main():
    inputs = processCLIArgs()
    # build math libs first
    makeMathLibs(inputs.j)
    tests = findTests(inputs.tests)
    if not tests:
        stopErr("No matching tests found.", -1)
    
    # compile all test models
    makeTest(mungeName("test/integration/compile_models_test"), inputs.j)
        


    #mathRunTests.mungeName = mungeName
    #mathRunTests.main()


if __name__ == "__main__":
    main()
