#!/usr/bin/env python

from __future__ import print_function
import argparse, json, os, platform, shutil, subprocess, sys, json, string
import pdfkit

_version = sys.version_info.major

if _version == 2: # Python 2.x:
    _input = raw_input
elif _version == 3: # Python 3.x:
    _input = input
else:
    raise Exception("Incompatible Python version")

def main(source_json, name_machine, output):
    if source_json == None:
        print("Invalid JSON file")
        sys.exit(1)

    try:
        json_data = json.load(open(source_json))
    except ValueError:
        print("Invalid JSON file")
        sys.exit(1)

    print("Detected {} packages".format(len(json_data)))
    packages = {}
    print("Parsing JSON packages")
    for package in json_data:
        pkg_name = package["name"]
        pkg_version = package["version"]
        pkg_hash = package["hash"]
        pkg_compiler = package["compiler"]["name"]
        pkg_compiler_version = package["compiler"]["version"]
        if pkg_name in packages.keys():
            packages[pkg_name].append({ "name": pkg_name, "version": pkg_version, "hash": pkg_hash, "compiler_name": pkg_compiler, "compiler_version": pkg_compiler_version })
        else:
            packages[pkg_name] = [{ "name": pkg_name, "version": pkg_version, "hash": pkg_hash, "compiler_name": pkg_compiler, "compiler_version": pkg_compiler_version }]

    
    print("Generating HTML")
    html_data = open("template/index.html").read()
    html_data = html_data.replace("{{name}}", name_machine)
    html_data = html_data.replace("{{count}}", str(len(packages)))

    table_records = ""

    index = 1
    for package in packages.keys():
        pkg = packages[package]
        table_records = append_table_record(table_records, pkg, package, index)
        index += 1

    html_data = html_data.replace("{{table_records}}", table_records)
    
    with open("template/base.html", "w+") as the_file:
        the_file.write(html_data)

    if not output.endswith(".pdf"):
        output += ".pdf"

    pdfkit.from_file("template/base.html", output, options={"enable-local-file-access": None, "orientation": "Landscape"})
    
    # print("Done")

def append_table_record(records, package, pkg_key, index):
    record = "{}{}".format(ws(20), "<tr>\n")
    record += "{}{}{}{}".format(ws(24), '<th scope="row">', index, "</th>\n")
    record += "{}{}{}{}".format(ws(24), '<td>', pkg_key, '</td>\n')
    record += "{}{}".format(ws(24), '<td>')
    ct = len(package)
    i = 1
    for itm in package:
        pkg_version = itm["version"]
        if i == ct:
            record += "{}".format(pkg_version)
        else:
            record += "{}<br>".format(pkg_version)
    record += "</td>\n"

    record += "{}{}".format(ws(24), '<td>')
    i = 1
    for itm in package:
        pkg_compiler_name = itm["compiler_name"]
        pkg_compiler_version = itm["compiler_version"]
        compiler = "{} {}".format(pkg_compiler_name, pkg_compiler_version)
        if i == ct:
            record += "{}".format(compiler)
        else:
            record += "{}<br>".format(compiler)
    record += "</td>\n"

    record += "{}{}".format(ws(24), '<td>')
    i=1
    for itm in package:
        pkg_name = itm["name"]
        pkg_version = itm["version"]
        pkg_hash = itm["hash"][:7]
        pkg_compiler_name = itm["compiler_name"]
        pkg_compiler_version = itm["compiler_version"]
        loader = "module load {}-{}-{}-{}-{}".format(pkg_name, pkg_version, pkg_compiler_name, pkg_compiler_version, pkg_hash)
        if i == ct:
            record += "{}".format(loader)
        else:
            record += "{}<br>".format(loader)
    record += "</td>\n"

    record += "{}{}".format(ws(24), '<td>')
    i=1
    for itm in package:
        pkg_hash = itm["hash"][:7]
        loader = "spack load \{}".format(pkg_hash)
        if i == ct:
            record += "{}".format(loader)
        else:
            record += "{}<br>".format(loader)
    record += "</td>\n"

    record += "{}{}".format(ws(20), '</tr>\n')
    records += record

    return records

def ws(i):
    return " " * i


def driver():
    parser = argparse.ArgumentParser(
        description="Reads Spack packages and converts to PDF."
    )
    parser.add_argument(
        "--source", "-s", dest="source_json", required=True, default=None,
        help="Source json output from spack find.")
    parser.add_argument(
        "--name", "-n", dest="name_machine", required=True, default=None,
        help="Name of the machine")
    parser.add_argument(
        "--output", "-o", dest="output", required=True, default=None,
        help="Output file destination (as PDF)")
    args = parser.parse_args()

    main(**vars(args))


if __name__ == "__main__":
    driver()
