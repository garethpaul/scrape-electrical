from __future__ import print_function

import argparse
import re
import sys
import urllib2
from urlparse import urljoin, urlparse


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
        try:
            self.cur.close()
        finally:
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


class DryRunDatabase(object):
    def __init__(self, output=None):
        self.output = output if output is not None else sys.stdout

    def insert(self, name, link, price):
        self.output.write('%s\t%s\t%s\n' % (name, link, price))

    def close(self):
        pass


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
        link_url = self.normalized_link(href)
        if link_url is None:
            return None

        price = product.find('span', {'class': 'price'})
        if price is None:
            return None

        price_text = price.text
        bold_price = price.find('b')
        if bold_price is not None:
            price_text = bold_price.text

        return (link.contents[0], link_url, price_text)

    def normalized_link(self, href):
        if not href or not href.strip():
            return None

        link_url = urljoin(self.url, href.strip())
        parsed_url = urlparse(link_url)
        if parsed_url.scheme not in ('http', 'https') or not parsed_url.netloc:
            return None

        return link_url

def build_arg_parser():
    parser = argparse.ArgumentParser(
        description='Scrape product rows from a permitted page.'
    )
    parser.add_argument('--url', required=True, help='source page URL to scrape')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='print parsed rows instead of writing to PostgreSQL'
    )
    parser.add_argument('--timeout', type=float, default=30, help='network timeout in seconds')
    parser.add_argument('--db-name', dest='db_name', help='PostgreSQL database name')
    parser.add_argument('--db-user', dest='db_user', help='PostgreSQL user')
    parser.add_argument('--db-password', dest='db_password', help='PostgreSQL password')
    parser.add_argument('--db-host', dest='db_host', help='PostgreSQL host')
    parser.add_argument('--table-name', dest='table_name', default='products', help='target table name')
    return parser


def parse_args(argv=None):
    return build_arg_parser().parse_args(argv)


def database_from_options(options):
    if options.dry_run:
        return DryRunDatabase()

    required_options = [
        ('--db-name', options.db_name),
        ('--db-user', options.db_user),
        ('--db-password', options.db_password),
        ('--db-host', options.db_host),
    ]
    missing_options = [name for name, value in required_options if not value]
    if missing_options:
        raise ValueError(
            'missing database options for live writes: %s' % ', '.join(missing_options)
        )

    return Database(
        options.db_name,
        options.db_user,
        options.db_password,
        options.db_host,
        options.table_name
    )


def run_cli(argv=None):
    parser = build_arg_parser()
    options = parser.parse_args(argv)
    try:
        database = database_from_options(options)
    except ValueError as error:
        parser.error(str(error))

    main(database, options.url, timeout=options.timeout)


def main(database, url, timeout=30):
    # put database with Product and include the url
    p = Product(database, url, timeout=timeout)
    # find products and place them in a database
    p.find()


if __name__ == '__main__':
    run_cli()
