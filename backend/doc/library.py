#!/usr/bin/env python

import os
import pathlib
import plistlib
import re

import bibtexparser
from bibtexparser.bwriter import BibTexWriter

library = pathlib.Path(os.environ['DROPBOX']).joinpath('research', 'library.bib')
survey = bibtexparser.bibdatabase.BibDatabase()
survey.entries = []

with open(str(library)) as bib:
    db = bibtexparser.load(bib)
    for comment in db.comments:
        if comment.startswith('BibDesk Static Groups{'): #}
            c = comment.replace("BibDesk Static Groups{\n", '').replace('}', '')
            static_groups = plistlib.loads(bytes(c, 'utf-8'))
    for g in static_groups:
        if g['group name'] == 'sgvis':
            cites = set(g['keys'].split(','))

    for article in db.entries:
        keys_to_drop = set()
        if article['ID'] in cites:
            if article.get('month'): keys_to_drop.add('month')
            for k in article.keys():
                if k.startswith('opt') or k.startswith('bdsk-') or k.startswith('date-'): keys_to_drop.add(k)
            for k in keys_to_drop: del article[k]
            survey.entries.append(article)

with open('library.bib', 'w') as bib:
    bib.write(BibTexWriter().write(survey))
