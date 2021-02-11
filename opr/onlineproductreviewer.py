from functools import partial
import time
import base64
import io
import urllib

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob

from .config import getValueOrDefault
from .oprexceptions import ReviewsUnavailableException
from .helper import GetPageSoup, isNotBlank, isEmpty, ToString, AsOne


class Review(object):

    def __init__(self, review):
        reviewTextBlob = TextBlob(review.strip())
        self.review = reviewTextBlob.correct()
        self.sentiment = reviewTextBlob.sentiment.polarity
        self.cloud = list(
            set([word.strip() for word, pos in reviewTextBlob.tags if pos == "JJ"]))

    def __repr__(self) -> str:
        return repr("{}, {}, {}".format(self.review, self.sentiment, self.cloud))

    @staticmethod
    def CalculateReviewCount(productCode):
        reviewCount = 0
        headers = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
        url = "https://www.amazon.in/product-reviews/{}/reviewerType=all_reviews/ref=cm_cr_arp_d_paging_btm_next_2?sortBy=recent&pageNumber=1".format(
            productCode)
        retryCount = 0
        while retryCount < getValueOrDefault("Requests", "RetryCount", 5):
            try:
                soup = GetPageSoup(headers, url)
                reviewCountDiv = soup.find_all(
                    'div', {'data-hook': 'cr-filter-info-review-rating-count'})
                reviewCount = [int(x) for x in reviewCountDiv[0].find(
                    'span').string.strip().replace(',', "").split() if x.isdigit()][-1]
            except IndexError:
                time.sleep(5)
                retryCount += 1

        return reviewCount

    @staticmethod
    def GetReviews(productCode, pageCount=5):
        reviews = []
        [reviews.extend(Review.GetReview(productCode, page)) for page in range(1, pageCount + 1)]
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
                soup = GetPageSoup(headers, url)
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
        self.reviewCount = Review.CalculateReviewCount(code)
        self.reviews = []
        self.sentiment = 0

    @staticmethod
    def GetProductName(code):
        return "None"

    def __repr__(self) -> str:
        return repr("{}, {}, {}".format(self.productCode, self.reviewCount, self.reviews))

    def __getCloud(self, width=800, height=800, bg_color='black', min_font=10):
        wordcloud = []
        [wordcloud.extend(r.cloud) for r in self.reviews]

        return WordCloud(width=width, height=height, background_color=bg_color,
                         min_font_size=min_font).generate(ToString(wordcloud))

    def cloudAsImage(self, width=800, height=800, bg_color='black', min_font=10):
        return self.__getCloud(width=width, height=height, bg_color=bg_color,
                               min_font=min_font).to_image()

    def cloudAsBase64(self, width=800, height=800, bg_color='black', min_font=10):
        cloud = self.__getCloud(width=width, height=height, bg_color=bg_color,
                                min_font=min_font)

        plt.imshow(cloud, interpolation='bilinear')
        plt.axis("off")

        image = io.BytesIO()
        plt.savefig(image, format='png')
        image.seek(0)  # rewind the data
        string = base64.b64encode(image.read())

        image_64 = 'data:image/png;base64,' + urllib.parse.quote(string)
        return image_64

    def updateReviews(self, reviewCount=50):
        pageCount = int(reviewCount / 10)
        reviews = Review.GetReviews(self.productCode, pageCount)
        self.reviews.extend([Review(review) for review in reviews])

    def updateSentiment(self):
        sentiment = sentimentCount = 0
        for r in self.reviews:
            sentiment += r.sentiment
            sentimentCount += 1
        self.sentiment = sentiment/sentimentCount


class ProductSearch(object):

    def __init__(self, productName):
        self.name = productName
