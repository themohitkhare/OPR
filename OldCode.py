'''
Contains methods to get reviews of a product, which is selected by the user in the Search.py module.
'''
from bs4 import BeautifulSoup
import time
import sys
import requests
from Ananlysis import Evaluation


def url(product, page):
    '''
    Takes product ID and page number, returns the url of the review page of the the
    given product.
    :param product:
    :param page:
    :return String:
    '''
    return "https://www.amazon.in/" + str(product[0]) + "/product-reviews/" + str(product[1]) + "/ref=cm_cr_arp_d_paging_btm_next_2?pageNumber=" + str(page)


def get_reviews(product, page):
    '''
    Takes product ID and the page number of the review, returns the list of all the reviews as string.
    :param product:
    :param page:
    :return List:
    '''
    reviewCount = 10 * page
    loadingCount = 0
    rlist = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    print("\nGetting Reviews..")
    for x in range(1, page + 1):
        sys.stdout.write("\r%d%%" % int(100 * (loadingCount / reviewCount)))
        sys.stdout.flush()

        source_code = ''
        while source_code == '':
            try:
                reviews = []
                link = url(product, x)
                source_code = requests.get(
                    link, headers=headers, verify=True).text
                soup = BeautifulSoup(source_code, 'html.parser')
                reviews = soup.find_all(
                    'span', {'class': 'a-size-base review-text review-text-content'})
                # comments = ''
                # for y in reviews:
                #     comments += y.string
                # soup = BeautifulSoup(source_code, 'html.parser')
                # reviews = soup.find_all('span')
                for y in reviews:
                    sys.stdout.write("\r%d%%" % int(
                        100 * (loadingCount / reviewCount)))
                    sys.stdout.flush()

                    loadingCount += 1
                    if y.text != None:
                        rlist.append(str(y.text))

            except Exception as e:
                # Sleep to deal with server blocks due to multiple requests.
                print(e)
                print("Retrying..")
                time.sleep(5)
                continue
        time.sleep(5)

    sys.stdout.write("\r%d%% Completed" % 100)
    sys.stdout.flush()
    print()
    return rlist


def review(product, feat, pagenum=5):
    '''
    Takes product ID, feature list and No. of Pages to search for reviews based on some specified
    features.
    Evaluates the comment/review based in the API (Text=Processing) and returns the Positive,Negative
    and Neutral evaluation and the overall sentiment of the users' reviews.
    :param product:
    :param feat:
    :param pnum:
    :return None:
    '''
    rlist = get_reviews(product, pagenum)
    reviewCount = 0
    posavg, negavg, neuavg = 0, 0, 0
    print("\nAnalysing Reviews..")
    for x in rlist:
        try:
            if len(feat) > 0:
                for y in feat:
                    if y in x:
                        sys.stdout.write("\r%d%%" % int(
                            100 * (reviewCount / len(rlist))))
                        sys.stdout.flush()
                        reviewCount += 1
                        evalu, pos, neg, neu = Evaluation(x)
                        posavg += float(pos)
                        negavg += float(neg)
                        neuavg += float(neu)
            else:
                sys.stdout.write("\r%d%%" % int(
                    100 * (reviewCount / len(rlist))))
                sys.stdout.flush()
                evalu, pos, neg, neu = Evaluation(x)
                posavg += float(pos)
                negavg += float(neg)
                neuavg += float(neu)
        except Exception as e:
            print(e)
            time.sleep(5)
    sys.stdout.write("\r%d%% Completed" % 100)
    sys.stdout.flush()
    tot = len(rlist)
    print("\n\nPositive: {:.2f} ".format(100 * posavg / tot))
    print("Negative: {:.2f} ".format(100 * negavg / tot))
    print("Neutral: {:.2f} ".format(100 * neuavg / tot))

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
            source_code = requests.get(
                p_string, headers=headers, verify=True).text
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

        reviewCount = int(soup.find_all(
            'span', {'class': 'a-size-medium totalReviewCount'})[0].string.replace(",", ""))
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

'''
Contains methods that executes a sentiment analysis of a given text and returns the result.
'''
from urllib import parse
import http.client
import json


def Evaluation(Article):
    '''
    Takes a string as input and returns the sentiment of the the string and probability of
    Positive, Negative and Neutral sentiment.
    :param Article:
    :return String, String, String, String:
    '''
    text = str(Article)
    # the input method to enter the text and parsing into required encoding
    para = {"text": text}
    data = parse.urlencode(para).encode()
    # print(data)
    # send a POST request to the sentimental analysis
    conn = http.client.HTTPConnection("text-processing.com")
    conn.request("POST", "http://text-processing.com/api/sentiment/", data)
    response = conn.getresponse()

    # Receiveing the JSON request and Displaying the results
    json_string = str(response.read())  # api/sentiment/
    # print(json_string)
    parsed_json = json.loads(json_string[2:-1])
    # print("\nReview : " + str(text))
    # print("\nEvaluation : " + parsed_json['label'])
    # print("Probability : ")
    # print("     Negative : " + str(parsed_json['probability']['neg']))
    # print("     Positive : " + str(parsed_json['probability']['pos']))
    # print("     Neutral  : " + str(parsed_json['probability']['neutral']))
    return [parsed_json['label'], str(parsed_json['probability']['pos']), str(parsed_json['probability']['neg']),
            str(parsed_json['probability']['neutral'])]
