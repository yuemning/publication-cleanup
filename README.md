# Publication Cleanup

A simple python script to help validate publication bibtex file and make changes whenever possible.

## Installation

Dependencies include `titlecase` and `bibtexparser`.

## Example Usage

`python validation.py example.bib -a example-author-list.txt -o example-output.bib`

The following is output to screen:
```
# Author list is provided...
Total number of authors: 2

# Detecting unrecognized or missing fields...
Beckham2019 has unrecognized field: (date: 2019-5-20)
# Please validate/remove the unrecognized fields in the above manually.

# Validating fields...
Beckham2019 entry's ID has been changed to lowercase beckham2019.
beckham2019 field data: (ENTRYTYPE: conference) has been changed to 'inproceedings'
beckham2019 has unrecognized author Levine, Adam
beckham2019 field: abstract wrapped at 79.
beckham2019 field: title wrapped at 79.
# Please verify author name list is in correct First Last format.
# Please verify the title is correcly capitalized.
# Please verify all the wrapping is correct.

# Please verify the following files are placed in the correct directory accordingly.
beckham2019:            :somepathtothefile.pdf:PDF
```
