from bs4 import BeautifulSoup
import time, sys
import requests
from Ananlysis import Evaluation


def url(product, page):
    '''
    Takes product ID and page number, returns the url of the review page of the the
    given product.
    :param product:
    :param page:
    :return:
    '''
    return "https://www.amazon.in/product-reviews/" + product + "/ref=cm_cr_getr_d_paging_btm_2?pageNumber=" + str(page)


def get_reviews(product, page):
    '''
    Takes product ID and the page number of the review, returns the list of all the reviews as string.
    :param product:
    :param page:
    :return:
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
                source_code = requests.get(url(product, x), headers=headers, verify=True).text
                soup = BeautifulSoup(source_code, 'html.parser')
                reviews = soup.find_all('span', {'class': 'a-size-base review-text'})
                for y in reviews:
                    sys.stdout.write("\r%d%%" % int(100 * (loadingCount / reviewCount)))
                    sys.stdout.flush()

                    loadingCount += 1
                    if y.string != None:
                        rlist.append(str(y.string))

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
    :return:
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
                        sys.stdout.write("\r%d%%" % int(100 * (reviewCount / len(rlist))))
                        sys.stdout.flush()
                        reviewCount += 1
                        evalu, pos, neg, neu = Evaluation(x)
                        posavg += float(pos)
                        negavg += float(neg)
                        neuavg += float(neu)
            else:
                sys.stdout.write("\r%d%%" % int(100 * (reviewCount / len(rlist))))
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
