import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from opr import Product

class TestProduct(unittest.TestCase):

    def test_product_creation(self):
        code = "B08L5VN68Y"
        product = Product(code)
        self.assertEqual(product.reviewCount, 244, "Should be Equal")


if __name__ == '__main__':
    unittest.main()