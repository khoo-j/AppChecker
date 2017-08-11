# AppChecker
Lightweight scraper to attain metadata from google store &amp; itunes

AppScraper by Jamie Khoo & Jonathan Lee @ GroupM NYC

Purpose:
Returns most app details from the App Store page: including (not exaustive) - Star Rating, number of raters, and content category. 
Google apps attained from webcrawling app webpage whilst iOS apps attained from iTunes API.

Usage:
Use command prompt to run python and this script, with the input file (required) & output file (optional) next to this module's name

Example usage:
>>> python AppScraper.py <filename.xlsx> <output_filename.xlsx>

If output filename is not specified, the default output name will be "AppScraper_Output.xlsx".

Compatibility:
Accepts .xlsx and .csv files. Outputs only into .xlsx file, because there are two sheets (iOS & Android).

License requires: Linking to source
