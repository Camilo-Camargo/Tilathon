#!/usr/bin/env python
# coding: utf-8
# In[13]:


try:
    #import import_ipynb
    import json
    import requests
    import re
    import sys
    import csv
    import os
    
    from bs4 import BeautifulSoup    
    from selenium import webdriver  
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC 
except Exception as e:
    print(e)


# # Debug
# Decorators for debugging individual functions.

# In[14]:


__DEBUG = True


# In[15]: 


def debug(_fun):
    def wrapper(*args, **kwargs):
        if(__DEBUG == True): print(f"[DEBUG ] {_fun.__qualname__}()")
        return _fun(*args, **kwargs)
    return wrapper

# clean 
@debug
def clean(text):
    return text.replace('$\xa0', '')


# # Driver
# The driver is `selenium`, allowing to interact with a browser to wait for some tags.

# In[16]:


class Driver:
    @debug
    def __init__(self, page, tags, config_tags=None):
        self.__url = page.url()
        self.__tags = tags
        self.__options = Options()
        self.__driver_path = "./driver/chromedriver"
        self.__config_tags = config_tags
    @debug
    def run(self):
        self.__driver = webdriver.Chrome(executable_path=self.__driver_path, options=self.__options)
    @debug
    def options(self, options):
        for option in options:
            self.__options.add_argument(option)
    @debug
    def driver_path(self, path):
        self.__driver_path = path
    @debug 
    def stop(self):
        self.__driver.close
    @debug
    def wait_class(self, tag, configs=None):
        try:
            self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, tag.value())))
            if(configs):
                for config in configs:
                    if config.function(config, self.__driver, tag): continue
                    else: wait_class(self, tag, configs=configs)
            return True
        except Exception as e:
            pass
        return False
    @debug
    def html(self):
        debug(self)
        driver = self.__driver
        driver.get(self.__url)
        
        for config in self.__config_tags:
            self.wait_class(config)
        
        for tag in self.__tags:
           self.wait_class(tag, configs=self.__config_tags)
        html = driver.page_source
        with open(f"./pages/{driver.title}.html", "w+") as f:
            f.write(html)
        self.stop()
        return html


# In[17]:


class Page:
    @debug
    def __init__(self, url, dynamic):
        self.__url = url
        self.__dynamic = dynamic
    @debug
    def url(self):
        return self.__url
    @debug
    def dynamic(self, dynamic=None):
        if dynamic: self.__dynamic = dynamic
        return self.__dynamic
    @debug 
    def fetch(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'
        }
        html = requests.get(self.__url, headers = headers)
        return html.content
    @debug
    def fetch_driver(self, tags, config_tags = None):
        driver = Driver(self, tags, config_tags = config_tags)
        driver.options([])
        driver.run()
        return driver.html()
    @debug
    def __str__(self):
        return f"Url: {self.__url} Dynamic: {self.__dynamic}"
    @debug
    def get_url(self):
        return self.__url


# In[18]:


class Tag:
    @debug
    def __init__(self, name,tag, value, children=None, count_tag=None, function=None):
        self.__name = name
        self.__tag = tag
        self.__value = value
        self.__function = function
    @debug
    def name(self):
        return self.__name
    @debug
    def tag(self):
        return self.__tag
    @debug
    def value(self):
        return self.__value
    @debug
    def function(self, *args, **kwargs):
        return self.__function(*args, **kwargs)
    @debug
    def __str__(self):
        return f"Name: {self.__name} Tag: {self.__tag} Value: {self.__value}"


# In[19]:


class Product:
    @debug
    def __init__(self,name, page, tag,tags):
        self.__page = page
        self.__tag = tag
        self.__tags = tags
        self.__name  = name
        self.__date  = None
        self.__price = None
        self.__scraped = False
        self.__product = {}
    @debug
    def scraped(self):
        return self.__scraped
    @debug
    def tags(self):
        return self.__tags
    @debug
    def fetch(self, locale = False): 
        if(locale):
            title = None
            while True:
                try:
                    html = self.__page.fetch() 
                    bs = BeautifulSoup(html, "lxml")
                    title = bs.find("title").get_text()
                except Exception as e: 
                    print(e)

                break

            try:
                with open(f"./pages/{title}.html") as f:
                    html = f.read()
            except FileNotFoundError:
                html = self.__page.fetch_driver(self.__tags, config_tags=self.__config_tags) 
            return html
        if(self.__page.dynamic() == 'True'):
            html = self.__page.fetch_driver(self.__tags, config_tags = self.__config_tags)
        else:
            html = self.__page.fetch()
        return html
    @debug
    def config_tags(self, config):
        self.__config_tags = config
    @debug
    def scrape(self, html):
        parent_tag = self.__tag
        product = self.__product
        bs = BeautifulSoup(html, 'lxml') 
        products = {}
        for parent in (bs.find_all(parent_tag.tag(), attrs={"class": parent_tag.value()})):
            for tag in self.__tags: 
                if(tag.name() not in products):
                    products[tag.name()] = []
                products[tag.name()].append(clean(parent.find(tag.tag(), attrs={"class": tag.value()}).get_text()))  

        return products

    @debug
    def __str__(self):
        return f"Product: {self.__name} Page: {self.__page}"


# In[20]:


class Store:
    @debug
    def __init__(self, name: str, page: Page):
        self.__name = name
        self.__page = page
    @debug
    def set_product(self, product):
        self.__product = product
    @debug
    def product(self):
        return self.__product

    @debug
    def name(self):
        return self.__name
    @debug
    def __str__(self):
        return f"Store: {self.__name} Page: {self.__page}"


# # Tags Configuration

# In[21]:


@debug
def __count_fun(config, driver, tag):
    pattern = re.compile('\d+')
    bs = BeautifulSoup(driver.page_source, 'lxml')
    count = bs.find(config.tag(), attrs={"class": config.value()}).span.get_text()
    count = int(re.search(re.compile(r"\d+"),count).group())
    count_len = bs.find_all(tag.tag(), attrs={'class': tag.value()})
    
    if len(count_len) > count:
        return True
    return False


# In[22]:


@debug
def load_stores(path):  
    global product
    stores = []

    with open(path, "r") as file:
        markets = json.load(file)
        for market in markets["stores"]:
            # Load Store Page
            page_json = market["page"]
            page = Page(page_json["url"], page_json["dynamic"])
            name = market["name"]
            store = Store(name, page)
            
            # Load Products to scrape
            product_json = market["product"]
            tags_json = product_json["tags"]
            page_product_json = product_json["page"]
            page_product_config_json = product_json["config"]
            page_product = Page(page_product_json["url"], page_product_json["dynamic"])
            tags = []
            
            config_tags = []
            
            for config in page_product_config_json:
               if("__count" == config["name"]):
                    config_tags.append(
                        Tag(config["name"], config["tag"], config["class"], children = config["children"], function = __count_fun)
                    )
            
            for tag in tags_json:
                tags.append(Tag(tag["name"], tag["tag"], tag["class"]))

            product_parent_tag_json = product_json["tag"] 
            product_parent_tag = Tag(
                product_parent_tag_json["name"],
                product_parent_tag_json["tag"],
                product_parent_tag_json["class"])

            product = Product(product_json["name"], page_product,product_parent_tag, tags)
            product.config_tags(config_tags)
            
            store.set_product(product)
            stores.append(store)
            
        return stores


# # Testing

# In[23]:
 

for store in load_stores("./items.json"):
    product = store.product()
    html = product.fetch() 

    items = product.scrape(html)

    #csv
    writer = None
    path = f"./csv/{store.name()}.csv"
   
    #headers
    headers = []
    headers.append("Retrieval Date")
    [headers.append(header) for header in items.keys()]


    isheader = True
    if(not os.path.isfile(path)):
        isheader = False 


    writer = csv.writer(open(path, "a+"))
    if(not isheader):
        writer.writerow(headers)


    #csv_headers
    import datetime
    for i in zip(*items.values()):
        writer.writerow((str(datetime.datetime.now()),*i))
