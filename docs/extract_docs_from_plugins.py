#!/usr/bin/python

#######################################################################
# This file is part of PyBlosxom.
#
# Copyright (c) 2011 Will Kahn-Greene
#
# PyBlosxom is distributed under the MIT license.  See the file
# LICENSE for distribution details.
#######################################################################

"""
This script generates documentation for plugins from the plugin docstrings.
"""

import os
import ast
import sys


# skip these because they're not plugins
SKIP = ("akismet.py", "__init__.py")


HELP = """extract_docs_from_plugins

This goes through the plugins in ../Pyblosxom/plugins/, extracts the
docstrings, and generates docs files for each one.  It puts them all in
a plugins/ directory here.

Docstrings for plugins should be formatted in restructured text.
"""


def get_info(node, info_name):
    # FIXME - this is inefficient since it'll traverse the entire ast
    # but we only really need to look at the top level.
    for mem in ast.walk(node):
        if not isinstance(mem, ast.Assign):
            continue

        for target in mem.targets:
            if not isinstance(target, ast.Name):
                continue

            if target.id == info_name:                
                return mem.value.s

    print "missing %s" % info_name
    return None


def build_docs_file(filepath):
    try:
        fp = open(filepath, "r")
    except (IOError, OSError):
        return False

    node = ast.parse(fp.read(), filepath, 'exec')

    title = " Plugin: %s " % os.path.splitext(os.path.basename(filepath))[0]
    body = ast.get_docstring(node, True)
    line = "=" * len(title)

    return "\n".join([line, title, line, "", body])


def save_entry(filepath, entry):
    parent = os.path.dirname(filepath)
    if not os.path.exists(parent):
        os.makedirs(parent)

    f = open(filepath, "w")
    f.write(entry)
    f.close()


def get_plugins(plugindir, outputdir):
    for root, dirs, files in os.walk(plugindir):
        # remove skipped directories so we don't walk through them
        for mem in SKIP:
            if mem in dirs:
                dirs.remove(mem)
                break

        for file_ in files:
            if ((file_.startswith("_") or not file_.endswith(".py") or
                 file_ in SKIP)):
                continue

            filename = os.path.join(root, file_)
            print "working on %s" % filename

            entry = build_docs_file(filename)

            output_filename = os.path.basename(filename)
            # output_filename = filename[len(plugindir):]
            # output_filename = output_filename.lstrip(os.sep)
            output_filename = os.path.splitext(output_filename)[0] + ".rst"
            output_filename = os.path.join(outputdir, output_filename)

            save_entry(output_filename, entry)


def main(args):
    print "update_registry.py"
    print args

    outputdir = "./plugins/"

    plugindir = "../Pyblosxom/plugins/"

    print "plugindir: %s" % plugindir
    if not os.path.exists(plugindir):
        print "Plugindir doesn't exist."
        sys.exit(1)

    print "outputdir: %s" % outputdir
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    get_plugins(plugindir, outputdir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
