#!/usr/bin/env python

# Parse sitemap xml files and save to csv
# @author Victor Angus <vjangus@gmail.com>
# python 2.7

import argparse
import lxml.etree
import os
import sys
import csv

from glob import glob
from urlparse import urlparse

# Get category
# Ex. https://www.example.com/Product/item.htm
# Category: Product
def get_category(url):
    parsed = urlparse(url).path.split('/')
    if len(parsed) >= 3:
        return parsed[1]
    return ''

parser = argparse.ArgumentParser()
parser.add_argument('sitemap_path', help='path to sitemap*.xml files', default='.')
parser.add_argument('sitemap_out', help='filename for csv output', default='sitemap.csv')
args = parser.parse_args()

# glob sitemap*.xml and read all
files=glob("%s/*.xml" % args.sitemap_path)

if len(files) <= 0:
    print >> sys.stderr, "Error: No sitemap xml files found!"
    sys.exit(1)

sitemap_out = args.sitemap_out
sitemap_urls_d = {}

for f in files:
    tree = lxml.etree.parse(f)
    root = tree.getroot()
    sitemap = os.path.basename(f)
    for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        if loc is not None and loc.text is not None:
            url2 = loc.text.strip()
        else:
            continue

        if url2:
            d = sitemap_urls_d.get(url2, {})
        else:
            continue

        # first occurrence
        if len(d) <= 0:
            d['category'] = get_category(url2)
            d['has_duplicates'] = 'no'
            d['sitemap_file'] = set()
            d['sitemap_file'].add(sitemap)
        # duplicate
        else:
            d['has_duplicates'] = 'yes'
            d['sitemap_file'].add(sitemap)

        sitemap_urls_d[url2] = d

urlid = 1

# write results
with open(sitemap_out, 'wb') as wfd:
    writer = csv.writer(wfd, quoting=csv.QUOTE_ALL)
    headers = ["urlid","url","category","has_duplicates","sitemap_file"]
    writer.writerow(headers)
    for url, d in sitemap_urls_d.items():
        sitemap = " ".join(d['sitemap_file'])
        row = [urlid, url, d['category'], d['has_duplicates'], sitemap]
        writer.writerow([unicode(s).encode("utf-8") for s in row])
        urlid += 1

# eof
