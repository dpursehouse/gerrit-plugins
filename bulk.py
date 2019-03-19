#!/usr/bin/env python

from __future__ import print_function
import argparse
import sys
from pygerrit2.rest import GerritRestAPI


def _main():
    descr = 'Perform bulk operations on Gerrit'
    parser = argparse.ArgumentParser(
        description=descr,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--gerrit-url', dest='url',
                        required=False,
                        default='https://gerrit-review.googlesource.com',
                        help='Gerrit URL')
    parser.add_argument('-q', '--query', dest='queries',
                        required=True, action='append',
                        help='query')
    parser.add_argument('-a', '--approve', dest='approve',
                        required=False, action='store_true',
                        help='apply Code-Review+2 to changes')
    parser.add_argument('-v', '--verify', dest='verify',
                        required=False, action='store_true',
                        help='apply Verified+1 to changes')
    parser.add_argument('-s', '--submit', dest='submit',
                        required=False, action='store_true',
                        help='submit changes')
    parser.add_argument('-f', '--filter', dest='filter',
                        required=False,
                        help='filter changes by project prefix')
    parser.add_argument('--abandon', dest='abandon',
                        required=False, action='store_true',
                        help='abandon changes')
    options = parser.parse_args()

    api = GerritRestAPI(url=options.url)
    query_terms = "%20".join(options.queries)
    changes = api.get("/changes/?q=" + query_terms)
    if options.filter:
        changes = [c for c in changes
                   if c["project"].startswith(options.filter)]
    print("Found %d changes" % len(changes))
    labels = {}
    review = {}
    if options.verify:
        labels['Verified'] = 1
    if options.approve:
        labels['Code-Review'] = 2
    if labels:
        review['labels'] = labels
    for change in changes:
        print("%s : %s" % (change["project"], change["subject"]))
        try:
            if options.abandon:
                api.post("/changes/%s/abandon" % change["id"])
                continue
            if review:
                api.post("/changes/%s/revisions/current/review" % change["id"],
                         json=review)
            if options.submit:
                api.post("/changes/%s/submit" % change["id"])
        except Exception as e:
            print("Operation failed: %s" % e, file=sys.stderr)


if __name__ == "__main__":
    _main()
