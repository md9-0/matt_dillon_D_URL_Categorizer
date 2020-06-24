#best practice q - when /where should i be importing things? should i never import something to main and function
# or is that ok?
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from base64 import urlsafe_b64encode
import hashlib
import requests
import json

import csv
import config
import pandas as pd

#i tried to do this to hide my key for github but i think i messed it up
access_key = config.access_key
secret_key = config.secret_key

#this seems like i'm overcomplicating, or is this the way to go?
def load_static_csv():
    with open(f'static/sites.csv') as csv_file:
        data = csv.reader(csv_file, delimiter=',')
        first_line = True
        wl_list = []
        for row in data:
            if not first_line:
                wl_list.append(row[0])
            else:
                first_line = False
    return(wl_list)

def upload_as_list(file):
    df = pd.read_csv(file)
    listver = df.iloc[:, 0].values.tolist()
    return listver

def check_present(url):
    with open('static/sites.csv', 'r') as readFile:
        check = "New"
        reader = csv.reader(readFile)
        for row in reader:
            for field in row:
                if field == url:
                    check = "Existing"
        return check



def write_to_static(url):
    if check_present(url) == "New":
        with open('static/sites.csv','a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([url])


def remove_from_static(url):
    status = f'has not been found in the whitelist, please try again'
    lines = list()
    with open('static/sites.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            lines.append(row)
            for field in row:
                if field == url:
                    status = 'has been removed from the whitelist'
                    lines.remove(row)
    with open('static/sites.csv', 'w',newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)
    return status
#what's the deal with UTF encoding other than i seemingly have to do it for this API
#this is ripped off I don't really get how it works
def webshrinker_categories_v3(access_key, secret_key, url=b"", params={}):
    params['key'] = access_key
    request = "categories/v3/{}?{}".format(urlsafe_b64encode(url).decode('utf-8'), urlencode(params, True))
    request_to_sign = "{}:{}".format(secret_key, request).encode('utf-8')
    signed_request = hashlib.md5(request_to_sign).hexdigest()

    return "https://api.webshrinker.com/{}&hash={}".format(request, signed_request)


#url = b"www.xaxis.com/"
def site_search(access_key, secret_key, url):
    api_url = webshrinker_categories_v3(access_key, secret_key, url)
    response = requests.get(api_url)
    status_code = response.status_code
    data = response.json()
    error_flag = f"API_Error - {status_code} -"


    if status_code == 200:
        # print(json.dumps(data, indent=4, sort_keys=True))
        # with open('data.txt', 'a') as outfile:
        #     json.dump(data, outfile,indent=4)
        #dataframe = pd.DataFrame.from_dict(data, orient="index")
        #return dataframe
        return data
    elif status_code == 202:
        return f'{error_flag} The website is being visited and the categories will be updated shortly'
    elif status_code == 400:
        return f'{error_flag} Bad or malformed HTTP request'
    elif status_code == 401:
        return f'{error_flag} Unauthorized - check your access and secret key permissions'
    elif status_code == 402:
        return f'{error_flag} Account request limit reached'
    else:
        return 'A general error occurred, try the request again'

def append_data(uploaded_urls):
    dfObj = pd.DataFrame()
    wl_list = load_static_csv()
    urlname = []
    wl =[]
    category = []
    iab = []
    for each in uploaded_urls:
        urlname.append(each)
        wl_check = each in wl_list
        wl.append(wl_check)
        bytekey = bytes(each, 'utf-8')
        result = site_search(access_key, secret_key, bytekey)
        if 'API_Error' in result:
            category.append(result)
            iab.append(result)
        else:
            add_static_cats(result)
            category.append(result["data"][0]["categories"][0]["label"])
            iab.append(result["data"][0]["categories"][0]["id"])
    dfObj['urlname'] = urlname
    dfObj['wl_check'] = wl_check
    dfObj['category'] = category
    dfObj['iab'] = iab
    return dfObj 

def update_cats(categories, site):
    try:
        df = pd.read_csv("static/categories.csv")
    except pd.errors.EmptyDataError: 
        df = pd.DataFrame.from_dict({
            'url': [],
            'category_id': [], 
            'label': [],
            'parent': [],
        })
    
    d = {
        'url': [],
        'category_id': [], 
        'label': [],
        'parent': [],
    }
    for category in categories:
        d['url'].append(site)
        d['category_id'].append(category['id'])
        d['label'].append(category['label'])
        d['parent'].append(category['parent'])
    df2 = pd.DataFrame.from_dict(d)
    result = pd.concat([df, df2])
    result.to_csv('static/categories.csv',index=False)

def add_static_cats(api_response):
    cats = api_response["data"][0]["categories"]
    site = api_response["data"][0]["url"]
    update_cats(cats, site)
    return [cats, site]