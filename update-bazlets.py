#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import re
from subprocess import call


def _main():
    descr = "Update bazlets revision"
    parser = argparse.ArgumentParser(
        description=descr, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-r", "--revision", dest="revision", required=True, help="bazlets revision"
    )
    parser.add_argument(
        "-b", "--branch", dest="branch", required=True, help="bazlets branch"
    )
    parser.add_argument(
        "-v", "--version", dest="version", required=False, help="gerrit API version"
    )
    options = parser.parse_args()
    workspace_filename = os.path.abspath("WORKSPACE")
    original_content = ""
    updated_content = ""
    with open(workspace_filename, "r") as workspace:
        original_content = workspace.read()
        updated_content = re.sub(r"[0-9a-f]{40}", options.revision, original_content)
    if updated_content != original_content:
        with open(workspace_filename, "w") as workspace:
            workspace.write(updated_content)
        if options.version:
            message = "Upgrade bazlets to latest %s to build with %s API" % (
                options.branch,
                options.version,
            )
        else:
            message = "Upgrade bazlets to latest %s" % options.branch
        call(["git", "commit", "-a", "-m", "%s" % message])


if __name__ == "__main__":
    _main()
