from bs4 import BeautifulSoup
import time
import requests

def product():
    prods = {}
    p_name = str(input("Enter Product Name: ")).strip().replace(" ","+")
    p_string = "https://www.amazon.in/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=" + p_name
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    source_code = ""
    while source_code == "":
        source_code = requests.get(p_string, headers = headers, verify=True).text
        soup = BeautifulSoup(source_code,'html.parser')
        products = soup.find_all('a', {'class':'a-link-normal s-access-detail-page s-color-twister-title-link a-text-normal'})
        for p in products:
            name = p.get('title')
            code = str(p.get('href')).split("//")
            if code[0] == 'https:':
                code = code[1].split("/")[3]
                prods[name] = code

    return prods

def features():
    prods = product()
    pind = {}
    val = 1
    for p in prods:
        print(val," ",p, " ", prods[p])
        pind[val] = prods[p]
        val += 1
    ind = input("Select a Product")
    print(prods[ind])
features()
