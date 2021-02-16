import base64
import io
import urllib
import datetime

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob

from .common import get_url_data_from_yaml, String, Array, Float, Integer, Product, Review, Dictionary


class AmazonReview(Review):

    def __init__(self, title, style, date, content, verified, helpful):
        reviewTextBlob = TextBlob(content.strip())
        self.title = String(title)
        self.content = String(reviewTextBlob.correct())
        self.sentiment = Float(reviewTextBlob.sentiment.polarity)
        self.word_cloud_list = Array(
            set([String(word).strip() for word, pos in reviewTextBlob.tags if pos == "JJ"]))

        self.style = self.__parseStyle(style)
        self.date = self.__parseDate(date)
        self.verified = verified
        self.helpful = helpful

    def __repr__(self) -> str:
        return repr("{}, {}, {}, {}".format(self.title, self.content, self.sentiment, self.verified))

    def __parseStyle(self, style):
        if style == None:
            return
        words = [[style[0]]]
        for c in style[1:]:
            if words[-1][-1].islower() and c.isupper():
                words.append(list(c))
            else:
                words[-1].append(c)

        words = Array([''.join(word) for word in words])
        return String(words.Last()) if words.Length() == 1 else words.Join()

    def __parseDate(self, date):
        return datetime.datetime.strptime(date.split('on')[-1].strip(), '%d %B %Y').strftime('%d/%m/%Y')


class AmazonProduct(Product):

    def __init__(self, code):
        self.productId = String(code)

        product_data = self.__getProductData()

        self.title = String(product_data['title'])
        self.style = String(product_data['style'])
        self.reviewCount = Array(
            String(product_data['reviewcount']).getDigits()).Last()

        self.stars = Dictionary()
        for rating in product_data['ratings']:
            if rating['star'] != None and rating['value'] != None:
                self.stars[String(rating['star']).ToInt()] = String(
                    rating['value']).ToInt()

        self.rating = Float(Array(
            [star*value for star, value in self.stars.items()]).Sum()/100).Round()

        self.reviews = Array()
        for review in product_data['reviews']:
            self.reviews.append(AmazonReview(
                review['title'], review['style'],
                review['date'], review['content'],
                review['verified'], review['helpful']))

        self.sentiment = Array(
            [review.sentiment for review in self.reviews]).Avg()

    def __getProductData(self) -> Dictionary:
        url = "https://www.amazon.in/product-reviews/{}/ref=cm_cr_arp_d_viewopt_srt?sortBy=recent&pageNumber=1".format(
            self.productId)
        return get_url_data_from_yaml(url, 'product.yml')

    def __repr__(self) -> str:
        return repr("{}, {}, {}".format(self.productId, self.reviewCount, self.reviews))

    def __getCloud(self, width=800, height=800, bg_color='black', min_font=10):
        wordcloud = Array()
        [wordcloud.extend(r.word_cloud_list) for r in self.reviews]

        return WordCloud(width=width, height=height, background_color=bg_color,
                         min_font_size=min_font).generate(wordcloud.ToString())

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


class ProductSearch(object):

    def __init__(self, productName):
        self.name = productName
