import re  
import sys 
import requests
from bs4 import BeautifulSoup  
import pandas as pd 
import matplotlib as plt 
import zlib   
import json

# user implementation 
from driver import *


# DEBUG VARIABLES
DEBUG = True
# function and caller 

class StaticPage: 
    """ 
    Save the all static pages with statics tags
    """
    def __init__(self, url, tags, driver = False): 
        self.driver = driver
 
        self.page = { 
            "url": url, 
            "html": None,
            "tags": tags,
            "info": []
        }

    def get(self):
        return self.page; 

    def set_html(self, html):
        self.page["html"] =  html

    def set_info(self, info):
        self.page["info"] = info


def parse_replace(text):
    """ 
    Replace a list of data to avoid it
    """ 
    replace = ["$\xa0"]
    for r in replace:
        text = text.replace(r,'')  
    return text


def parse_html_tags( bs: BeautifulSoup, tags: [], f = None):
    """
    Parse the tags and if there is need more actions pass a function, f
    """  
    data_tags = []
    for tag in tags:
        #print('data_tags.append([', tag[0], 'bs.find_all(', tag[1], ',', "attrs={'class':", tag[2],'})])') 
        data_tags.append([
            tag[0], 
            [parse_replace(text.get_text()) for text in bs.find_all(tag[1], attrs={'class': tag[2]})]
        ])
    return data_tags



def parse_html_(pages):
    """ 
    Parses all pages and save your html
    """
    for page in pages:  
        html = page.get()["html"]
        url = page.get()["url"] 
        if(html):  
            if(DEBUG): print(f"[PARSE]: {url}")
            bs = BeautifulSoup(html, 'lxml'); 
            #[TODO]: check the returns 
            info = parse_html_tags(bs, page.get()['tags'])
            page.set_info(info) 


def html_decode(html, algorithm):  
    pass

def fetch_html(pages): 
    """ 
    Gets all the pages 
    """ 

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'
    } 

    for page in pages: 
        url = page.get()["url"]



        if(page.driver):  
            if(DEBUG): print(f"[FETCH DRIVER]: {url}")
            html = driver_get_html(url, page.get()['tags']) 

        else: 
            if(DEBUG): print(f"[FETCH]: {url}")
            html = requests.get(url, headers = headers)  

            if(html.status_code == 200):
                if(DEBUG): print(f"[FETCH]: DONE")
            else:
                if(DEBUG): print(f"[SKIP]: {url}")
                continue;

            if(DEBUG): print(f"[PRINTING]: {html.headers}") 
            html = html.content 
        # Check encoding
 
        #compress_algorithm = html.headers["content-encoding"] 
        #if( compress_algorithm ):
        #    html = html_decode(html.content, compress_algorithm)
        #else:
        page.set_html(html) 
        
def parse_data_frame(data):   
    table = []
    titles = []

    for tag in data: 
        k = 0
        titles.append(tag[0])     

        for item in tag[1]:
            if(len(table)-1 < k):
                table.append([]) 

            table[k].append(item) 
            k += 1 

    df = pd.DataFrame(table, columns = titles)
    print(df) 


def main():  
    static_pages = [] 

    with open("items.json", "r") as file:
        markets = json.load(file) 
    for market in markets.values():
        static_pages.append(StaticPage(market["url"], market["tags"], market["driver"]))

    fetch_html(static_pages)
    parse_html_(static_pages)
    for page in static_pages:
        parse_data_frame(page.get()["info"])


if(__name__ == "__main__"):
    main()
