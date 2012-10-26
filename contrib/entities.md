
Using the entities spreadsheet
==============================

The entities spreadsheet contains a list of all actors (of any kind) mentioned in 
the source data - that includes the registered represenatitives, their legal and 
executive representatives, organisations who are members of registered reps, 
clients named in the financial statements and those entities referred to in the 
textual networking section of the register entries. 

The table has a number of columns, but the key fields are: 

* ``etlFingerPrint`` - the source name of the entity as represented in the data.
* ``canonicalName`` - the cleaned up name. See below for conventions. 

Some other columns are: 

* ``countryCode`` - the contact country for the entry, only for representatives. 
* ``etlTable`` - the class of the entity. 
* ``legalStatus`` - the legal form of the entry, only for representatives. 
* ``normalizedForm`` - canonicalName without any special characters.
* ``reverseForm`` - the reverse of the text. sorting by this will effectively sort 
  by acronym.

When working with the spreadsheet, please make sure to adhere to these formal 
rules:

* Never edit ``etlFingerPrint``. 
* All edits to columns other than ``etlFingerPrint`` and ``canonicalName`` are 
  disregarded.
* Make sure the file is encoded as ``utf-8``.

With this out of the way, here's the rules:

* To map several entities to the same name, put in the same ``canonicalName``. 
  This is relatively particular about identity, so upper/lowercase, trailing 
  spaces and missing accents are all significant.
* We're trying to come to a normalized name form. It is:

    [Name] [Legal] [(Acronym)]

  Examples:

    Bund Deutscher Industrieller e.V. (BDI)
    Friends of the Earth Europe (FoEE)

* Apply the normal form even if not doing it sounds better.
* Don't overinterpret it. If something is a three-letter acronym for which 
  multiple interpreations exist - let's leave it for the moment.

Other rules I would propose are:

* If something has a French/German/... and an English name, let's use the 
  English one even if it is less commonly used. 
* This is not a place for politics. If A is a sock puppet for Y, leave them 
  separate - we will find another way to express this. 
* The goal is to join legal entities. Brussels offices are separate from their 
  companies if they are incorporated separately (e.g. AmCham vs. AmCham EU).


