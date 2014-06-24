# SolrUpdater: a program to extract textual data from a database, de-identify that textual data, and upload it to a dual-core Apache/Solr index

## This program

1- extracts textual data from a database
2- performs limited cleaning (strip RTF format) and tokenization of these texts
3- de-identifies (i.e. replaces personally identifiable information with generic placeholders) these texts
4- pushes the result to a dual-core Apache/Solr index

## Usage of monthlyUpdate.py

There a three basic parameters: OFFLOAD_START, OFFLOAD_END and a True or False to indicate whether the texts need to be de-identified or not.

Example usage:
> python src/monthlyUpdate.py 01/2001 02/2001 False

## Usage of DeIdentifier.py

The de-identification works independently of the other parts of SolrUpdater.

Example usage:
> echo "This is a name, Marc. Can you please de-identify it?" | python src/DeIdentifier.py

The de-identification works with gazetteers. These need to be filled with (first) names, street names, city names for the algorithm to work effectively.

