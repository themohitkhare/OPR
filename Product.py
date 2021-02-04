from Config import config, getValueOrDefault
from OPRExceptions import ProductReviewCountUnavailableException, ReviewsUnavailableException
from Helper import isNotBlank, isEmpty, ToString, AsOne

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
from bs4 import BeautifulSoup
import multiprocessing
from functools import partial
import time
import requests


class Review(object):

    def __init__(self, review):
        reviewTextBlob = TextBlob(review.strip())
        self.review = reviewTextBlob.correct()
        self.sentiment = reviewTextBlob.sentiment.polarity
        self.cloud = list(set([word.strip() for word, pos in reviewTextBlob.tags if pos == "JJ"]))

    def __repr__(self) -> str:
        return repr("{}, {}, {}".format(self.review, self.sentiment, self.cloud))

    @staticmethod
    def CalculateReviewCount(productCode):
        headers = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
        url = "https://www.amazon.in/product-reviews/{}/reviewerType=all_reviews/ref=cm_cr_arp_d_paging_btm_next_2?sortBy=recent&pageNumber=1".format(
            productCode)
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

    @staticmethod
    def GetReviews(productCode, pageCount=5):
        reviews = []
        with multiprocessing.Pool(processes=getValueOrDefault("System", "ParallelProcessCount", 40)) as pool:
            pages = list(range(1, pageCount + 1))
            func = partial(Review.GetReview, productCode)
            reviews.extend(pool.map(func, pages))
        return AsOne(reviews)

    @staticmethod
    def GetReview(productCode, pageNumber):
        reviews = []
        headers = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
        url = "https://www.amazon.in/product-reviews/{}/reviewerType=all_reviews/ref=cm_cr_arp_d_paging_btm_next_2?sortBy=recent&pageNumber={}".format(
            productCode, pageNumber)
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
                        reviews.append(comment)
                if isEmpty(commentSpans):
                    raise ReviewsUnavailableException
                else:
                    break
            except ReviewsUnavailableException:
                time.sleep(getValueOrDefault(
                    "Requests", "RetrySleepTimer", 5))
                retryCount += 1
        return reviews


class Product(object):

    def __init__(self, code: str):
        self.productCode = code
        self.ratingCount, self.reviewCount = Review.CalculateReviewCount(code)
        self.reviews = [Review(review) for review in Review.GetReviews(code)]

    def __repr__(self) -> str:
        return repr("{}, {}, {}, {}".format(self.productCode, self.ratingCount, self.reviewCount, self.reviews))

    def showCloud(self):
        wordcloud = []
        for review in self.reviews:
            wordcloud.extend(review.cloud)
        cloud = WordCloud(width=800, height=800,
                          background_color='white',
                          min_font_size=10).generate(ToString(wordcloud))

        plt.figure(figsize=(8, 8), facecolor=None)
        plt.imshow(cloud)
        plt.axis("off")
        plt.tight_layout(pad=0)

        plt.show()
