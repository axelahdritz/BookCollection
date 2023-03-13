import os
import string
from pathlib import Path
import re

def rmdir(directory):
    directory = Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()
    directory.rmdir()

def clean_page(page):
    chunks = re.split('\n\n', page)
    paragraph_chunks = []
    for chunk in chunks:
        # check for chapter title
        if len(chunk) < 10:
            paragraph_chunks.append(chunk)
        elif re.search('[?.!]', chunk[-1]):
            paragraph_chunks.append(chunk)
        else:
            new_chunk = chunk + '.'
            paragraph_chunks.append(new_chunk)
    # check for chapter headings after removing punctuation
    hyphen_flag = 0
    heading_flag = 1
    footnote_flag = 0
    previous = ''
    to_keep = []
    for chunk in chunks:
        if len(chunk) == 0:
            continue
        if footnote_flag == 1:
            continue
        if heading_flag == 1:
            heading = chunk.translate(str.maketrans('', '', string.punctuation)).split(' ')
            heading = ''.join(heading)
            capitals = 0
            noncapitals = 0
            for i in [*heading]:
                if re.search('^[0-9A-Z]+$', i):
                    capitals += 1
                else:
                    noncapitals += 1
            if re.search('^[0-9A-Z]+$', heading):
                continue
            elif capitals > noncapitals:
                continue
            else:
                heading_flag = 0
        if re.search('^(\[|\|)(.?)BLANKSIDA(.?)(\]|\|)$', chunk):
            continue
        if re.search('^[ ]*[0-9]+[ ]*[A-Z]', chunk):
            footnote_flag = 1
            continue
        if hyphen_flag == 1:
            chunk = ''.join([previous, chunk])
            hyphen_flag = 0
        if chunk[-1] == '-':
            hyphen_flag = 1
            previous = chunk[:-1]
            continue
        if re.search('[!#$%&()*+,-.:;<=>?@[\\]^_{|}~]{2}',chunk[-2:]):
            chunk = chunk[:-1]
        if not chunk.isdigit():
            to_keep.append(chunk)
    if footnote_flag:
        final_fixed = []
        for item in to_keep:
            lst = item.split()
            fixed = []
            for i in lst:
                if re.search('^[a-zA-Z.]+[0-9]$', i):
                    fixed.append(i[:-1])
                elif re.search('^[a-zA-Z.]+[0-9]{2}$', i):
                    fixed.append(i[:-2])
                elif re.search('^[a-zA-Z.]+[0-9]{3}$', i):
                    fixed.append(i[:-3])
                else:
                    fixed.append(i)
            final = ' '.join(fixed)
            final_fixed.append(final)
        string_final = " ".join(final_fixed)
    else:
        string_final = " ".join(to_keep)
    return string_final, hyphen_flag

def clean_document(document):
    full_document = []
    hyphen = 0
    previous_page = ''
    for page in document:
        cleaned_page, hyphen_flag = clean_page(page)
        if hyphen:
            cleaned_page = ''.join([previous_page,cleaned_page])
            hyphen = 0
        if hyphen_flag:
            hyphen = 1
            previous_page = cleaned_page
        else:
            full_document.append(cleaned_page)
    return full_document

def is_page_empty(page):
    chunks = re.split('\n', page)
    empty = []
    for chunk in chunks:
        if len(chunk) == 0:
            continue
        if re.search('^(\[|\|)(.?)BLANKSIDA(.?)(\]|\|)$', chunk):
            continue
        if not chunk.isdigit():
            empty.append(chunk)
    string_final = " ".join(empty)
    if len(string_final) == 0:
        is_empty = True
    else:
        is_empty = False
    return is_empty