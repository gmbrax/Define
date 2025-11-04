# Define

Define is a CLI-based Dictionary and Thesaurus tool that uses the Merriam-Webster API

This Application requires an API key from Merriam-Webster that can be acquired [here](https://dictionaryapi.com/)[^1].

[^1]: Limitations Apply on usage

## Instalation
To install the application, you'll need python 3.11 or higher and pip
To install the application, you'll need to create a venv or install globally( although not recommended)
To create a venv please issue inside the cloned folder : 
```python3 -m venv .venv ```
and then issue:
``` source .venv/bin/activate```
And finally to install Define please issue:
``` pip isntall -e . ```

## Usage
To run the application you can just issue:
``` define ``` and you will be prompted to enter the word to be defined.

By default, issuing ```define ``` you will fetch both the dictionary and thesaurus definition.

If you want to fetch either the thesaurus or dictionary, you will need to issue a flag, for example,
if you wish to fetch only thesaurus, you can issue: ```define - t``` and conversely for only dictionary 
you can issue:```define -d ```

