from abc import abstractmethod
import os
from time import time
from PIL.Image import Image
import requests

from wordcloud import WordCloud
import selectorlib


from .config import getValueOrDefault
from .oprexceptions import DataRequestError


class Integer(int):
    pass


class Float(float):
    def Round(self, precision=2):
        return Float(round(self, precision))


class Dictionary(dict):
    pass


class String(str):

    def isBlank(self) -> bool:
        return self is None or self == "" or len(self) == 0

    def isNotBlank(self) -> bool:
        return not self.isBlank()

    def hasNumbers(self) -> bool:
        if self.isNotBlank():
            return any(char.isdigit() for char in self)
        return False

    def startsWith(self, ch: str) -> bool:
        if self.isNotBlank() and String(ch).isNotBlank:
            return self[0:len(ch)] == ch
        return False

    def endsWith(self, ch: str) -> bool:
        if self.isNotBlank and String(ch).isNotBlank():
            return self[-1*len(ch):] == ch
        return False

    def ToInt(self) -> Integer:
        return Array([s for s in self if s.isdigit()]).ToInt()

    def getDigits(self):
        return [int(x) for x in self.strip().replace(',', "").split() if x.isdigit()]


class Array(list):
    def isEmpty(self) -> bool:
        return len(self) == 0 or self is None

    def isNotEmpty(self) -> bool:
        return not self.isEmpty()

    def ToString(self) -> String:
        return " ".join(self)

    def AsOne(self):
        result = Array()
        [result.extend(array) for array in self]
        return result

    def ToInt(self) -> Integer:
        return Integer(self.Join(""))

    def Avg(self):
        return Float(round(sum(self)/self.Length(), 2))

    def Sum(self):
        return Float(sum(self))

    def Length(self):
        return self.__len__()

    def Last(self):
        return self[-1]

    def Join(self, delimiter=" "):
        return String(delimiter).join(self)


class Review(object):

    def __init__(self):
        self._title = None
        self._content = None
        self._sentiment = None
        self._word_cloud_list = None
        self._images = None

    @property
    def title(self) -> String:
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @title.deleter
    def title(self):
        del self._title

    @property
    def content(self) -> String:
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @content.deleter
    def content(self):
        del self._content

    @property
    def sentiment(self) -> String:
        return self._sentiment

    @sentiment.setter
    def sentiment(self, value):
        self._sentiment = value

    @sentiment.deleter
    def sentiment(self):
        del self._sentiment

    @property
    def word_cloud_list(self) -> String:
        return self._word_cloud_list

    @word_cloud_list.setter
    def word_cloud_list(self, value):
        self._word_cloud_list = value

    @word_cloud_list.deleter
    def word_cloud_list(self):
        del self._word_cloud_list

    @property
    def images(self) -> String:
        return self._images

    @images.setter
    def images(self, value):
        self._images = value

    @images.deleter
    def images(self):
        del self._images


class Product(object):

    def __init__(self):
        self._productId = None
        self._title = None
        self._reviewcount = None
        self._reviews = None
        self._sentiment = None
        self._content = None
        self._rating = None

    @property
    def productId(self) -> String:
        return self._productId

    @productId.setter
    def productId(self, value):
        self._productId = value

    @productId.deleter
    def productId(self):
        del self._productId

    @property
    def title(self) -> String:
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @title.deleter
    def title(self):
        del self._title

    @property
    def reviewcount(self) -> Integer:
        return self._reviewcount

    @reviewcount.setter
    def reviewcount(self, value):
        self._reviewcount = value

    @reviewcount.deleter
    def reviewcount(self):
        del self._reviewcount

    @property
    def reviews(self) -> Array:
        return self._reviews

    @reviews.setter
    def reviews(self, value):
        self._reviews = value

    @reviews.deleter
    def reviews(self):
        del self._reviews

    @property
    def sentiment(self) -> Float:
        return self._sentiment

    @sentiment.setter
    def sentiment(self, value):
        self._sentiment = value

    @sentiment.deleter
    def sentiment(self):
        del self._sentiment

    @property
    def content(self) -> String:
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @content.deleter
    def content(self):
        del self._content

    @property
    def rating(self) -> Float:
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = value

    @rating.deleter
    def rating(self):
        del self._rating

    @abstractmethod
    def __getProductData(self) -> Dictionary:
        raise NotImplementedError

    @abstractmethod
    def __getWordCloud(self, width, height, bg_color, min_font_size) -> WordCloud:
        raise NotImplementedError

    @abstractmethod
    def wordCloudAsImage(self, width, height, bg_color, min_font_size) -> Image:
        raise NotImplementedError

    @abstractmethod
    def wordCloudAsBase64(self, width, height, bg_color, min_font_size):
        raise NotImplementedError


# Soup cache implementation
def get_url_data_from_yaml(url, yaml_file):
    extractor = selectorlib.Extractor.from_yaml_file(
        os.path.join(os.path.dirname(__file__), "selectors", yaml_file))
    data = None
    retryCount = 0
    retry = True
    headers = {
        'authority': 'www.amazon.in',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'scheme': 'https',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.63',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    while retryCount < getValueOrDefault("Requests", "RetryCount", 5) and retry:
        try:
            session = requests.Session()
            session.headers = headers
            request = session.get(url)
            data = Dictionary(extractor.extract(request.text, base_url=url))
            session.close()
            retry = False
        except Exception as ex:
            time.sleep(5)
            retryCount += 1
    if data is None:
        raise DataRequestError
    return data
