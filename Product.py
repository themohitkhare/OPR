from OPRExceptions import *
from Helper import *

import jamspell

from bs4 import BeautifulSoup
import time
import requests


class Review(object):

    spellChecker = jamspell.TSpellCorrector()
    spellChecker.LoadLangModel("Models/en.bin")

    def __init__(self, review):
        self.review = self.GetFixedReview(review)

    def __repr__(self) -> str:
        return self.review

    def GetFixedReview(self,  review):
        return Review.spellChecker.FixFragment(review.strip())


class Product(object):

    def __init__(self, code: str):
        self.productCode = code
        self.ratingCount, self.reviewCount = self.CalculateReviewCount()
        self.reviews = []

    def __repr__(self) -> str:
        return repr("{}, {}, {}, {}".format(self.productCode, self.ratingCount, self.reviewCount, self.reviews))

    def CalculateReviewCount(self):
        headers = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
        url = "https://www.amazon.in/product-reviews/{}/reviewerType=all_reviews/ref=cm_cr_arp_d_paging_btm_next_2?sortBy=recent&pageNumber=1".format(
            self.productCode)
        retryCount = 0
        while retryCount < getValueOrDefault("Requests", "RetryCount", 5):
            try:
                session = requests.Session()
                session.headers['User-Agent'] = headers
                soup = BeautifulSoup(session.get(url).content, 'html.parser')
                reviewCountDiv = soup.find_all(
                    'div', {'data-hook': 'cr-filter-info-review-rating-count'})
                return [int(x) for x in reviewCountDiv[0].find('span').string.strip().replace(',', "").split() if x.isdigit()]
            except IndexError:
                time.sleep(5)
                retryCount += 1

        raise ProductReviewCountUnavailableException

    def GetReviews(self, pageCount: int = 10):
        headers = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
        for page in range(1, pageCount+1):
            url = "https://www.amazon.in/product-reviews/{}/reviewerType=all_reviews/ref=cm_cr_arp_d_paging_btm_next_2?sortBy=recent&pageNumber={}".format(
                self.productCode, page)
            retryCount = 0
            while retryCount < getValueOrDefault("Requests", "RetryCount", 5):
                try:
                    session = requests.Session()
                    session.headers['User-Agent'] = headers
                    soup = BeautifulSoup(session.get(
                        url).content, 'html.parser')
                    commentSpans = soup.find_all(
                        'span', {'class': 'a-size-base review-text review-text-content'})
                    for commentSpan in commentSpans:
                        comment = commentSpan.find('span').string
                        if isNotBlank(comment):
                            self.reviews.append(Review(comment))
                    if isEmpty(commentSpans):
                        raise ReviewsUnavailableException
                    else:
                        break
                except ReviewsUnavailableException:
                    time.sleep(getValueOrDefault(
                        "Requests", "RetrySleepTimer", 5))
                    retryCount += 1
