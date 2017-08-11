"""
AppScraper by Jamie Khoo & Jonathan Lee @ GroupM NYC

Purpose:
Returns most app details from the App Store page: including (not exaustive) - Star Rating, number of raters, and content category. 
Google apps attained from webcrawling app webpage whilst iOS apps attained from iTunes API.

Usage:
Use command prompt to run python and this script, with the input file (required) & output file (optional) next to this module's name

>>> python AppScraper.py <filename.xlsx> <output_filename.xlsx>

If output filename is not specified, the default output name will be "AppScraper_Output.xlsx".

Compatibility:
Accepts .xlsx and .csv files. Outputs only into .xlsx file, because there are two sheets (iOS & Android).

Change log:
5/5/2017: Error handling for empty google or itunes table
5/6/2017: Error handling for numpy int type
"""

import requests
import json
import sys
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime

def passback(var):
    '''Check if html value is present'''
    if var is None:
        return "N/A"
    else:
        return var

def get_playstore_info(app):
    '''Handler for google app IDs'''
    build_url = "https://play.google.com/store/apps/details?id={}".format(app)
    app_page = requests.get(build_url)
    soup = BeautifulSoup(app_page.content, 'html.parser')

    title = passback(soup.find('div', class_ = 'id-app-title'))
    author = passback(soup.find("span", itemprop = "name"))
    author_url = passback(soup.find("a", class_="dev-link"))
    url = passback(soup.find("meta", itemprop= "url"))
    last_update = passback(soup.find("div", class_="content", itemprop = "datePublished"))
    downloads_range = passback(soup.find("div", itemprop= "numDownloads"))
    rating = passback(soup.find("meta", itemprop= "ratingValue"))
    rated_by = passback(soup.find("meta", itemprop= "ratingCount"))
    c_rating = passback(soup.find("div", class_="content", itemprop = "contentRating"))
    content_category = passback(soup.find("span", itemprop = "genre"))

    #Optional variables
    top = passback(soup.find("span", class_="badge-title"))
    ads = passback(soup.find("span", class_="ads-supported-label-msg"))
    r_reason = passback(soup.find("div", class_="content", itemprop = "contentRating"))
    rate_reason = passback(r_reason.find_next_sibling('div')) if r_reason != 'N/A' else r_reason

    #Populate dictionary fields
    gog_details = dict()
    gog_details['App.Android.Raw.ID'] = app
    gog_details['App.Android.Raw.AppName'] = title.text if title != "N/A" else title
    gog_details['App.Android.Raw.Author'] = author.text if author != "N/A" else author
    gog_details['App.Android.Raw.Link'] = url['content'] if url != "N/A" else url
    gog_details['App.Android.Raw.LastUpdate'] = datetime.strptime((last_update.text),"%B %d, %Y").strftime("%m/%d/%Y") if last_update != "N/A" else last_update
    gog_details['App.Android.Raw.DownloadRange'] = downloads_range.text.strip() if downloads_range != "N/A" else downloads_range
    gog_details['App.Android.Raw.StarRating'] = round(float(rating['content']),2) if rating != "N/A" else rating
    gog_details['App.Android.Raw.RatingVolume'] = rated_by['content']if rated_by != "N/A" else rated_by
    gog_details['App.Android.Raw.AgeRating'] = c_rating.text if c_rating != "N/A" else c_rating
    gog_details['App.Android.Raw.RatingReasonString'] = rate_reason.text if rate_reason != 'N/A' else rate_reason
    gog_details['App.Android.Raw.TopDeveloper'] = top.text if top != 'N/A' else "N/A"
    gog_details['App.Android.Raw.AdSupported'] = ads.text.strip() if ads != 'N/A' else "N/A"
    gog_details['App.Android.Raw.ContentCategory'] = content_category.text if content_category != 'N/A' else "N/A"
    try:
        gog_details['App.Android.Raw.AuthorURL'] = str(author_url).split('=')[3].split('&')[0].split('/')[2] if author_url != "N/A" else author_url
    except IndexError:
        gog_details['App.Android.Raw.AuthorURL'] = author_url.text
    except:
        gog_details['App.Android.Raw.AuthorURL'] = 'Error'
    for cell in soup.findAll('div', class_ =  'title'):
        if 'Offered' in cell.text:
            offered_by = passback(cell.find_next_sibling('div'))
            gog_details['App.Android.Raw.Seller'] = offered_by.text if offered_by != "N/A" else offered_by

    return gog_details

def get_itunes_info(app):
    '''Handler for Apple app IDs'''
    build_url = "https://itunes.apple.com/lookup?id={}".format(app)
    app_page = requests.get(build_url)
    soup = BeautifulSoup(app_page.content, 'html.parser')
    d_soup = json.loads(str(soup))

    app_details = dict()
    app_details['App.iOS.Raw.ID'] = app
    if d_soup['results']:
        d = d_soup['results'][0]

        app_details['App.iOS.Raw.AppName'] = d.get('trackName','N/A')
        app_details['App.iOS.Raw.Author'] = d.get('artistName','N/A')
        app_details['App.iOS.Raw.Seller'] = d.get('sellerName','N/A')
        app_details['App.iOS.Raw.Link'] = d.get('trackViewUrl','N/A')
        app_details['App.iOS.Raw.AgeRating'] = d.get('contentAdvisoryRating','N/A')
        app_details['App.iOS.Raw.Language'] = d.get('languageCodesISO2A','N/A')
        app_details['App.iOS.Raw.EnglishFlag'] = "Yes" if "EN" in d.get('languageCodesISO2A','N/A') else "No"
        app_details['App.iOS.Raw.RateReasonString'] = d.get('advisories','N/A')

        #Fields with transformation required
        seller = d.get('sellerUrl','N/A')
        star = d.get('averageUserRating','N/A')
        rating_v = d.get('userRatingCount','N/A')
        l_update = d.get('currentVersionReleaseDate','N/A')
        genre = d.get('genres','N/A')

        app_details['App.iOS.Raw.AuthorURL'] = seller.split('/', 2)[2] if seller != 'N/A' else seller
        app_details['App.iOS.Raw.StarRating'] = round(star,2) if star != 'N/A' else star
        app_details['App.iOS.Raw.RatingVolume'] = int(rating_v) if rating_v != 'N/A' else rating_v
        app_details['App.iOS.Raw.LastUpdate'] = datetime.strptime(l_update,"%Y-%m-%dT%H:%M:%SZ").strftime("%m/%d/%Y") if l_update != 'N/A' else l_update
        app_details['App.iOS.Raw.CategoryString'] = genre[0] if genre != 'N/A' else genre

    else:
        for i in ['AppName','Author','Seller','AuthorURL','Link','LastUpdate','StarRating','RatingVolume','AgeRating',
        'CategoryString','Language', 'EnglishFlag','RateReasonString']:
            s = 'App.iOS.Raw.' + i
            app_details[s] = "N/A"

    return app_details


def main():
    start_time = time.time()

    if sys.argv[1].endswith('.xlsx'):
        test = pd.read_excel(sys.argv[1])
    elif sys.argv[1].endswith('.csv'):
        test = pd.read_csv(sys.argv[1])
    else:
        print ("Usage: In command prompt (Win) or bash (Mac/Linux), type 'python AppScraper.py <input_filename>'")

    sites = test['site'].tolist()

    google = []
    itunes = []

    for i in sites:
        print ("Working on: " + str(i))
        if isinstance(i,np.integer) or isinstance(i, int):
            itunes.append(get_itunes_info(str(i)))
        elif isinstance(i,str):
            google.append(get_playstore_info(i))
        else:
            print ("Failure at: {}".format(i))

    itunes = pd.DataFrame(itunes)
    google = pd.DataFrame(google)

    try:
        output = sys.argv[2]
    except IndexError:
        output = 'AppScraper_Output.xlsx'

    outputz = pd.ExcelWriter(output, engine='xlsxwriter')

    if itunes.empty:
        print ('ALERT: No Apple ID provided. No Apple sheet will be provided')

    else:
        itunes = itunes[['App.iOS.Raw.ID','App.iOS.Raw.Author','App.iOS.Raw.AuthorURL','App.iOS.Raw.CategoryString',
        'App.iOS.Raw.AgeRating','App.iOS.Raw.Language','App.iOS.Raw.LastUpdate','App.iOS.Raw.RateReasonString',
        'App.iOS.Raw.RatingVolume','App.iOS.Raw.StarRating','App.iOS.Raw.Seller','App.iOS.Raw.AppName','App.iOS.Raw.Link']]
        itunes.to_excel(outputz, sheet_name='Apple_Apps', index=False)

    if google.empty:
        print ('ALERT: No Google ID provided. No Google sheet will be provided')

    else:
        google = google[['App.Android.Raw.ID','App.Android.Raw.AdSupported','App.Android.Raw.Author','App.Android.Raw.AuthorURL',
        'App.Android.Raw.ContentCategory','App.Android.Raw.AgeRating','App.Android.Raw.DownloadRange','App.Android.Raw.LastUpdate',
        'App.Android.Raw.Seller','App.Android.Raw.RatingReasonString','App.Android.Raw.RatingVolume','App.Android.Raw.StarRating',
        'App.Android.Raw.AppName','App.Android.Raw.TopDeveloper','App.Android.Raw.Link']]
        google.to_excel(outputz, sheet_name='Google_Apps', index=False)
    
    outputz.save()
    outputz.close()
    print("%f seconds" % (time.time() - start_time))

if __name__ == '__main__':
    main()