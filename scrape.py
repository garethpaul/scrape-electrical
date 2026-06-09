import re
import urllib2

class Database(object):
    """
    This is the database class for a postgres database. This posts based on parsed arguments
    """
    def __init__(self, dbname, dbuser, dbpassword, dbhost, tbname):
        # Set variables for class database
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.dbhost = dbhost
        self.tbname = tbname
        import psycopg2
        self.conn = psycopg2.connect(
            user=self.dbuser,
            password=self.dbpassword,
            host=self.dbhost,
            dbname=self.dbname
        )
        self.cur = self.conn.cursor()

    def close(self):
        # Over psycopg2 must be closed
        self.cur.close()
        self.conn.close()

    def insert(self, name, link, price):
        table_name = self.safe_table_name()
        self.cur.execute(
            "INSERT INTO %s (p_name, p_link, p_price) VALUES (%%s, %%s, %%s)" % table_name,
            (name, link, self.normalized_price(price))
        )
        self.conn.commit()

    def safe_table_name(self):
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', self.tbname):
            raise ValueError('unsafe table name: %s' % self.tbname)
        return self.tbname

    def normalized_price(self, price):
        return price.replace('$', '').strip()

class Product(object):
    """
    The product class is for handling products to find and insert
    """
    def __init__(self, database, url, timeout=30):
        # Set variables for class product.
        self.database = database
        self.url = url
        if timeout <= 0:
            raise ValueError('timeout must be positive')
        self.timeout = timeout

    def read(self):
        opener = urllib2.build_opener()
        return opener.open(self.build_request(), timeout=self.timeout).read()

    def build_request(self):
        return urllib2.Request(self.url)

    def find(self):
        # find products via self.url and argument --url 
        try:
            from bs4 import BeautifulSoup
            page = BeautifulSoup(self.read())
            self.find_products(page)
        finally:
            self.database.close()

    def find_products(self, page):
        for product in page.findAll('div', {'class':'zg_item_normal'}):
            fields = self.product_fields(product)
            if fields is None:
                continue

            self.database.insert(name=fields[0], link=fields[1], price=fields[2])

    def product_fields(self, product):
        title = product.find('div', {'class': 'zg_title'})
        if title is None:
            return None

        link = title.find('a')
        if link is None or not link.contents:
            return None

        try:
            href = link['href']
        except KeyError:
            return None
        if not href or not href.strip():
            return None

        price = product.find('span', {'class': 'price'})
        if price is None:
            return None

        price_text = price.text
        bold_price = price.find('b')
        if bold_price is not None:
            price_text = bold_price.text

        return (link.contents[0], href.strip(), price_text)

def main(database, url):
    # put database with Product and include the url
    p = Product(database, url)
    # find products and place them in a database
    p.find()
