'''
Module contain methods that return products based on a query and search each review of the user for some given features.
'''
from bs4 import BeautifulSoup
import time
import requests
from Reviews import review, url


def product():
    '''
    Returns the list of products based on the query or item entered bt the user.
    :return List:
    '''
    prods = {}
    p_name = str(input("Enter Product Name: ")).strip().replace(" ", "+")
    p_string = "https://www.amazon.in/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=" + p_name
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    source_code = ""
    while source_code == "":
        try:
            source_code = requests.get(p_string, headers=headers, verify=True).text
        except Exception as e:
            print(e)
            time.sleep(5)
            print("Retrying..")
            continue
        soup = BeautifulSoup(source_code, 'html.parser')
        products = soup.find_all('a', {
            'class': 'a-link-normal a-text-normal'})
        for p in products:
            ch = p.get('href').split('/')[1]
            if (ch == 'gp') == False:
                info = p.get('href').split('/')
                name = info[1]
                code = info[3]
                prods[name] = code

    return prods


def features():
    '''
    A simply function to get the features of the the specified product and transfer them to the
    review package to search for the defined features in the the comments.
    if left blank i.e. no feature specified it will return a black list.
    :return None:
    '''
    prods = product()
    pind = {}
    val, page, reviewCount = 1, 5, 0
    for p in prods:
        print(val, " ", p, " ", prods[p])
        pind[val] = (p, prods[p])
        val += 1
    ind = int(input("Select a Product: "))
    feat = str(input("Enter Features: ")).split(" ")

    try:
        # Getting the total number of Reviews available.
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        url = "https://www.amazon.in/" + pind[ind][0] + "/product-reviews/" + \
            pind[ind][1] + "/ref=cm_cr_arp_d_paging_btm_next_2?pageNumber=1"
        source_code = requests.get(url, headers=headers, verify=True).text
        soup = BeautifulSoup(source_code, 'html.parser')

        reviewCount = int(soup.find_all('span', {'class': 'a-size-medium totalReviewCount'})[0].string.replace(",", ""))
        print("Total Reviews Found: {}".format(reviewCount))
        maxPage = int(reviewCount / 10) if reviewCount / 10 >= 1 else 1
        page = int(input("Enter Pages(Max: {}) : ".format(maxPage)))

    except Exception as e:
        print(e)
        print("Retrying..")
        time.sleep(5)
    if reviewCount < 1:
        print("No review found!")
        exit(0)
    else:
        review((pind[ind][0], pind[ind][1]), feat, page)
    # sleep for delaying result in CommandLine.
    # time.sleep(10000)

features()
