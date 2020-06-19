#!/usr/bin/env python

from __future__ import print_function
import argparse
import sys
from pygerrit2.rest import GerritRestAPI

COMMANDS = "DOWNLOAD_COMMANDS"
REVISION = "CURRENT_REVISION"


def _main():
    descr = "Perform bulk operations on Gerrit"
    parser = argparse.ArgumentParser(
        description=descr, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-u",
        "--gerrit-url",
        dest="url",
        required=False,
        default="https://gerrit-review.googlesource.com",
        help="Gerrit URL",
    )
    parser.add_argument(
        "-q", "--query", dest="query", required=True, action="store", help="query"
    )
    parser.add_argument(
        "-o",
        "--option",
        dest="options",
        required=False,
        action="append",
        help="query options",
    )
    parser.add_argument(
        "-c",
        "--commands",
        dest="commands",
        required=False,
        action="store_true",
        help="how to fetch changes; appends -o " + REVISION + " -o " + COMMANDS,
    )
    parser.add_argument(
        "-a",
        "--approve",
        dest="approve",
        required=False,
        action="store_true",
        help="apply Code-Review+2 to changes",
    )
    parser.add_argument(
        "-v",
        "--verify",
        dest="verify",
        required=False,
        action="store_true",
        help="apply Verified+1 to changes",
    )
    parser.add_argument(
        "-s",
        "--submit",
        dest="submit",
        required=False,
        action="store_true",
        help="submit changes",
    )
    parser.add_argument(
        "-f",
        "--filter",
        dest="filter",
        required=False,
        help="filter changes by project prefix",
    )
    parser.add_argument(
        "-fs",
        "--subject",
        dest="subject",
        required=False,
        help="filter changes by subject prefix",
    )
    parser.add_argument(
        "--abandon",
        dest="abandon",
        required=False,
        action="store_true",
        help="abandon changes",
    )
    parser.add_argument(
        "--hashtag",
        dest="hashtags",
        required=False,
        action="append",
        help="add hashtags",
    )
    parser.add_argument(
        "-r",
        "--reviewer",
        dest="reviewers",
        required=False,
        action="append",
        help="add reviewers",
    )
    options = parser.parse_args()

    api = GerritRestAPI(url=options.url)
    query_terms = options.query.replace(" ", "%20")
    uri = "/changes/?q=" + query_terms
    query_options = [o.upper() for o in options.options] if options.options else []
    if options.commands:
        if REVISION not in query_options:
            query_options.append(REVISION)
        if COMMANDS not in query_options:
            query_options.append(COMMANDS)
    if query_options:
        uri += "".join(["&o=%s" % o for o in query_options])
    changes = api.get(uri)
    changes_count = len(changes)
    print("Found %d changes" % changes_count)
    if options.filter:
        changes = [c for c in changes if c["project"].startswith(options.filter)]
    if options.subject:
        changes = [c for c in changes if c["subject"].startswith(options.subject)]
    filtered_count = len(changes)
    if filtered_count < changes_count:
        print("Filtered out %d changes" % (changes_count - filtered_count))
    labels = {}
    review = {}
    if options.reviewers:
        review["reviewers"] = [{"reviewer": r} for r in options.reviewers]
    if options.verify:
        labels["Verified"] = 1
    if options.approve:
        labels["Code-Review"] = 2
    if labels:
        review["labels"] = labels
    for change in changes:
        print("%s : %s" % (change["project"], change["subject"]))
        try:
            if options.hashtags:
                hashtags = {"add": options.hashtags}
                api.post("/changes/%s/hashtags" % change["id"], json=hashtags)
            if options.abandon:
                api.post("/changes/%s/abandon" % change["id"])
                continue
            if review:
                api.post(
                    "/changes/%s/revisions/current/review" % change["id"], json=review
                )
            if options.submit:
                api.post("/changes/%s/submit" % change["id"])
        except Exception as e:
            print("Operation failed: %s" % e, file=sys.stderr)
    if options.commands:
        for change in changes:
            repo = change["project"].split("/")[-1]
            command = next(iter(change["revisions"].values()))["fetch"]["http"][
                "commands"
            ]["Checkout"]
            print("cd %s && %s && cd -" % (repo, command))


if __name__ == "__main__":
    _main()
