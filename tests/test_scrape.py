import unittest

import scrape


class FakeCursor(object):
    def __init__(self):
        self.calls = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params))


class FakeConnection(object):
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1


class FakeProductDatabase(object):
    def __init__(self):
        self.inserts = []

    def insert(self, name, link, price):
        self.inserts.append((name, link, price))


class FakeAnchor(object):
    def __init__(self, name, href):
        self.contents = [name]
        self.href = href

    def __getitem__(self, key):
        if key == 'href':
            return self.href
        raise KeyError(key)


class FakeTitle(object):
    def __init__(self, anchor):
        self.anchor = anchor

    def find(self, tag):
        if tag == 'a':
            return self.anchor
        return None


class FakeTextNode(object):
    def __init__(self, text):
        self.text = text


class FakePrice(object):
    def __init__(self, text, bold_text=None):
        self.text = text
        self.bold = FakeTextNode(bold_text) if bold_text is not None else None

    def find(self, tag):
        if tag == 'b':
            return self.bold
        return None


class FakeProductNode(object):
    def __init__(self, name=None, href=None, price_text=None, bold_price=None):
        self.title = None
        self.price = None
        if name is not None and href is not None:
            self.title = FakeTitle(FakeAnchor(name, href))
        if price_text is not None:
            self.price = FakePrice(price_text, bold_price)

    def find(self, tag, attrs=None):
        if tag == 'div' and attrs == {'class': 'zg_title'}:
            return self.title
        if tag == 'span' and attrs == {'class': 'price'}:
            return self.price
        return None


class FakePage(object):
    def __init__(self, products):
        self.products = products

    def findAll(self, tag, attrs=None):
        if tag == 'div' and attrs == {'class':'zg_item_normal'}:
            return self.products
        return []


def database_with(table_name):
    database = scrape.Database.__new__(scrape.Database)
    database.tbname = table_name
    database.cur = FakeCursor()
    database.conn = FakeConnection()
    return database


class DatabaseTests(unittest.TestCase):
    def test_insert_uses_parameterized_values(self):
        database = database_with('products')

        database.insert("ACME's plug", 'https://example.test/item', '$12.34')

        self.assertEqual(1, len(database.cur.calls))
        sql, params = database.cur.calls[0]
        self.assertEqual(
            'INSERT INTO products (p_name, p_link, p_price) VALUES (%s, %s, %s)',
            sql,
        )
        self.assertEqual(("ACME's plug", 'https://example.test/item', '12.34'), params)
        self.assertEqual(1, database.conn.commits)

    def test_insert_rejects_unsafe_table_name(self):
        database = database_with('products; DROP TABLE products')

        self.assertRaises(ValueError, database.insert, 'name', 'link', '$1.00')


class ProductParserTests(unittest.TestCase):
    def test_find_products_inserts_bold_and_plain_prices(self):
        database = FakeProductDatabase()
        product = scrape.Product(database, 'https://example.test/source')
        page = FakePage([
            FakeProductNode('Wire stripper', ' https://example.test/wire ', '$10.00', '$8.50'),
            FakeProductNode('Outlet cover', 'https://example.test/cover', ' $2.25 '),
        ])

        product.find_products(page)

        self.assertEqual(
            [
                ('Wire stripper', 'https://example.test/wire', '$8.50'),
                ('Outlet cover', 'https://example.test/cover', ' $2.25 '),
            ],
            database.inserts,
        )

    def test_find_products_skips_incomplete_products(self):
        database = FakeProductDatabase()
        product = scrape.Product(database, 'https://example.test/source')
        page = FakePage([
            FakeProductNode('Missing price', 'https://example.test/item'),
            FakeProductNode(price_text='$3.00'),
        ])

        product.find_products(page)

        self.assertEqual([], database.inserts)


if __name__ == '__main__':
    unittest.main()
