from bs4 import BeautifulSoup
import time
import requests
from Ananlysis import Evaluation

def url(product,page):
    return "https://www.amazon.in/product-reviews/"+ product + "/ref=cm_cr_getr_d_paging_btm_2?pageNumber=" +str(page)


def get_reviews(product,page):
    rlist = []
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    for x in range(1,page+1):
        print("Review page " + str(x))
        source_code = ''
        while source_code == '':
            try:
                source_code = requests.get(url(product,x),headers = headers, verify=True).text
                soup = BeautifulSoup(source_code, 'html.parser')
                reviews = soup.find_all('span', {'class': 'a-size-base review-text'})
                for y in reviews:
                    rlist.append(str(y.string))

            except Exception as e:
                print(e)
                print("Retrying..")
                time.sleep(5)
                continue
        time.sleep(5)

    return rlist


product = "B071DF166C"
list = get_reviews(product,5)
posavg,negavg,neuavg = 0,0,0
for x in list:
    try:
        evalu,pos,neg,neu = Evaluation(x)
        posavg += float(pos)
        negavg += float(neg)
        neuavg += float(neu)
    except:
        time.sleep(5)
tot = len(list)
print(posavg/tot)
print(negavg/tot)
print(neuavg/tot)

