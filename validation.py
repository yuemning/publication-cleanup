# In order to run this file, please install bibtexparser, titlecase.
# Both of them can be installed through pip.

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import author, page_double_hyphen
import re
from titlecase import titlecase
import textwrap

import argparse
parser = argparse.ArgumentParser(description="Validate bibtex entries.")
parser.add_argument('bibtex_file', type=str,
                    help='path to the bibtex file')
parser.add_argument('-o', dest="output_file", default='processed_bibtex.bib',
        help='path to the output bibtex file (default: processed_bibtex.bib)')
parser.add_argument('-a', dest="author_list_file",
        help='path to the publications author list txt file')
args = parser.parse_args()


# Initialize text wrapper for abstracts
wrapper = textwrap.TextWrapper(initial_indent="    ", subsequent_indent="    ")
wrapper.width = 79

# Copied from source, and change 'keyword' to 'keywords'
# ref: https://bibtexparser.readthedocs.io/en/master/_modules/bibtexparser/customization.html#keyword
def keyword(record, sep=',|;'):
    """
    Split keyword field into a list.

    :param record: the record.
    :type record: dict
    :param sep: pattern used for the splitting regexp.
    :type record: string, optional
    :returns: dict -- the modified record.

    """
    if "keywords" in record:
        record["keywords"] = [i.strip() for i in re.split(sep, record["keywords"].replace('\n', ''))]

    return record

# Let's define a function to customize our entries.
# It takes a record and return this record.
def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    #  record = type(record)
    record = author(record)
    #  record = editor(record)
    #  record = journal(record)
    record = keyword(record)
    #  record = link(record)
    record = page_double_hyphen(record)
    #  record = doi(record)
    return record

with open(args.bibtex_file) as bibtex_file:
    parser = BibTexParser()
    parser.customization = customizations
    bib_database = bibtexparser.load(bibtex_file, parser=parser)


authors = None

if args.author_list_file:
    print("# Author list is provided...")
    with open(args.author_list_file) as author_file:
        authors = author_file.read().splitlines()
    print("Total number of authors: {}".format(len(authors)))
    print("")
    #  print(authors[0])
    #  print(authors[1])

#  ============================================================
#  ENTRY FORMAT

#  @[type]{[citation key],
#    [field name] = {[field value]},
#    [field name] = {[multiline
#                    field value]},
#    ...
#    [field name] = {
#      [long paragraph
#      of text]
#    },
#    [field name] = {[field value]}
#  }

#  entry type, citation key, and field names in lowercase
#  no blank lines
#  maximum line length 79 characters [except file field]

#  use @inproceedings, not @conference
#  citation key in the form [last name][year][optional letter]

#  single spaces around '=', do not align field values
#  field values enclosed in braces, not quotes
#  each field terminated with a comma, except the last field

#  authors in [first middle last] format except when [von] or [jr]
#  see https://nwalsh.com/tex/texhelp/bibtx-23.html

# =============================================
#  ENTRY SORTING

#  TODO: section off entries by year

#  TODO: The following can be achieved with writer.order_entries_by(...)
#  TODO: within each year, sort entries
#    by first author
#    then by subsequent authors
#    then by title

#  within each entry, sort fields
#    author, title, [collection], [publisher], [date], [other]
#    collection = journal, booktitle, edition, editor,
#                 volume, number, series, chapter, pages
#    publisher = publisher, organization, institution, school, address
#    date = year, month
#    other = keywords, abstract, file


special_fields = ['ID', 'ENTRYTYPE']
# NOTE: Make sure the following fields are listed in the expected display order
fields = ['author',
'title',
# collection
'journal',
'booktitle',
'edition',
'editor',
'volume',
'number',
'series',
'chapter',
'pages',
# publisher
'publisher',
'organization',
'institution',
'school',
'address',
# date
'year',
'month',
# other
'keywords',
'abstract',
'file']

# The following fields will be wrapped according to multiline format
# The 'abstract' field will be wrapped according to long paragraph of text
multiline_fields = ['author',
'title',
# collection
'journal',
'booktitle',
'edition',
'editor',
'volume',
'number',
'series',
'chapter',
'pages',
# publisher
'publisher',
'organization',
'institution',
'school',
'address',
# date
'year',
'month',
# other
'keywords',
#  'abstract',
#  'file'
]



print("# Detecting unrecognized or missing fields...")

must_exist_fields = ['title', 'author', 'year', 'file', 'abstract']
# Makes sure the fields are recognized by us, and output fields not in the included list
# Also check certain fields must exist
has_unrecognized = False
has_missing = False
for entry in bib_database.entries:
    ID = entry['ID']
    #  if 'author' in entry:
    #      print(entry['author'])
    #  if 'keywords' in entry:
    #      print(entry['keywords'])
    for key, val in entry.items():
        if key not in fields + special_fields:
            print("{} has unrecognized field: ({}: {})".format(ID, key, val))
            has_unrecognized = True
        #  print(key, val)
    for key in must_exist_fields:
        if key not in entry:
            print("{} is missing field: {}".format(ID, key))
            has_missing = True

if has_unrecognized:
    print("# Please validate/remove the unrecognized fields in the above manually.")
if has_missing:
    print("# Please add the missing fields in the above manually.")
print("")



print("# Validating fields...")

def get_first_last_name(a):
    """Returns the name in First Last format.

    Args:
        a (str): Name in Last, First format.
    """

    terms = a.split(", ")
    #  print(terms)
    # If the following assertion fails, probably some name has more than first, last name
    assert(len(terms) == 2)
    return terms[1] + ' ' + terms[0]

def get_last_name(a):
    """Returns the last name.

    Args:
        a (str): Name in Last, First format.
    """

    terms = a.split(", ")
    #  print(terms)
    # If the following assertion fails, probably some name has more than first, last name
    assert(len(terms) == 2)
    return terms[0]



field_type={
        "ENTRYTYPE": ['inproceedings', 'phdthesis', 'mastersthesis', 'article'],
        }
# Check that each field satisfies the correct format
for entry in bib_database.entries:
    ID = entry['ID']
    if not ID.islower():
        new_ID = ID.lower()
        print("{} entry's ID has been changed to lowercase {}.".format(ID, new_ID))
        ID = new_ID
        entry['ID'] = ID
    for key, val in entry.items():
        if key in field_type:
            if val not in field_type[key]:
                # Special case: if used @conference, change to @inproceedings
                if val == 'conference':
                    entry['ENTRYTYPE'] = 'inproceedings'
                    print("{} field data: ({}: {}) has been changed to 'inproceedings'".format(ID, key, val))
                else:
                    print("{} field data is unrecognized: ({}: {})".format(ID, key, val))
    if authors is not None:
        if 'author' in entry:
            author = entry['author']
            for a in author:
                if not a in authors:
                    print("{} has unrecognized author {}".format(ID, a))
                if 'von' in a or 'jr' in a:
                    print("{} has author {} with 'von' or 'jr'".format(ID, a))
    if 'author' in entry and 'year' in entry:
        first_author = entry['author'][0]
        expected_id = get_last_name(first_author).lower() + entry['year']
        if expected_id not in ID:
            print("{} is different than the expected ID: {}<optional letter>".format(ID, expected_id))
    if 'author' in entry:
        author = entry['author']
        first_author = get_first_last_name(author[0])
        author_string = first_author
        for a in author[1:]:
            author_string = author_string + ' and ' + get_first_last_name(a)
        entry['author'] = author_string
    if 'keywords' in entry:
        keywords = entry['keywords']
        keywords_string = keywords[0]
        for k in keywords[1:]:
            keywords_string = keywords_string + ', ' + k
        if not keywords_string.islower():
            print("{} keywords are not all lowercase: {}".format(ID, keywords_string))
        entry['keywords'] = keywords_string
    if 'title' in entry:
        title = entry['title']
        capital_title = titlecase(title)
        entry['title'] = capital_title
    if 'abstract' in entry:
        abstract = entry['abstract']
        abstract_paragraphs = abstract.split('\n')
        #  print(len(abstract_paragraphs[0]))
        if len(abstract_paragraphs[0]) > 79:
            print("{} field: abstract wrapped at 79.".format(ID))
        #  print(len(abstract_paragraphs))
        wrapped_texts = ""
        for abst in abstract_paragraphs:
            splitted_abstract = wrapper.wrap(abst)
            #  print(wrapper.wrap(abstract))
            wrapped_text = ""
            for text in splitted_abstract:
                wrapped_text = wrapped_text + "\n" + text
            wrapped_texts = wrapped_texts + wrapped_text + "\n"
        # FIXME: hacking so that the ending bracket for abstract has indent of 2 spaces
        wrapped_texts += "  "
        entry['abstract'] = wrapped_texts
    for key, val in entry.items():
        if key in multiline_fields:
            if "\n" in val:
                print("{} field: {} already has linebreak, skiping wrap check.".format(ID, key))
            else:
                prefixed_val = "  {} = [".format(key) + val
                if len(prefixed_val) > 79:
                    print("{} field: {} wrapped at 79.".format(ID, key))
                    index = prefixed_val.index('[')
                    subsequent_indent = ' '
                    for i in range(index):
                        subsequent_indent += ' '
                    tmp_wrapper = textwrap.TextWrapper(initial_indent="", subsequent_indent=subsequent_indent)
                    tmp_wrapper.width = 79
                    splitted_texts = tmp_wrapper.wrap(prefixed_val)
                    wrapped_text = ""
                    for text in splitted_texts:
                        wrapped_text = wrapped_text + "\n" + text
                    wrapped_text = wrapped_text[index+2:]
                    entry[key] = wrapped_text


print("# Please verify author name list is in correct First Last format.")
print("# Please verify the title is correcly capitalized.")
print("# Please verify all the wrapping is correct.")



# Output the file location, so that user can check that they are correct
print("\n# Please verify the following files are placed in the correct directory accordingly.")

for entry in bib_database.entries:
    ID = entry['ID']
    if 'file' in entry:
        filepath = entry['file']
        print("{}:\t\t{}".format(ID, filepath))
    else:
        print("{} has not specified a file! Fix first.".format(ID))



# Specify the writer, including indent and display order
writer = BibTexWriter()
#  writer.contents = ['comments', 'entries']
#  writer.order_entries_by = ('ID', )
writer.indent = '  '
writer.display_order = tuple(fields)
bibtex_str = bibtexparser.dumps(bib_database, writer)

with open(args.output_file, 'w') as bibtex_file:
    bibtexparser.dump(bib_database, bibtex_file, writer)
