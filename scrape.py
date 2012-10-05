from lib import url
from bs4 import BeautifulSoup
import psycopg2
import argparse
import random
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
        self.conn = psycopg2.connect("user=%s password=%s host=%s dbname=%s" % (self.dbuser, self.dbpassword, self.dbhost, self.dbname))
        self.cur = self.conn.cursor()

    def close(self):
        # Over psycopg2 must be closed
        self.conn.close()
        self.cur.close()

    def insert(self, name, link, price):
        self.cur.execute("INSERT INTO " + self.tbname + " (p_name, p_link, p_price) VALUES ('" + name + "','" + link + "','" + price.replace('$', '') + "')")
        self.conn.commit()
        
class Product(object):
    """
    The product class is for handling products to find and insert
    """
    def __init__(self, database, url):
        # Set variables for class product.
        self.database = database
        self.url = url

    def read(self):
        req = urllib2.Request(self.url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.212.0 Safari/532.0')
        req.add_header('Referer', 'http://www.google.com/url?sa=t&source=web&ct=res&cd=7')
        req.add_header('DNT', random.choice([1,0]))               
        opener = urllib2.build_opener()
        return opener.open(req).read()

    def find(self):
        # find products via self.url and argument --url 
        page = BeautifulSoup(self.read())
        for product in page.findAll('div', {'class':'zg_item_normal'}):
            p = product.find('div', {'class': 'zg_title'}).find('a')
            p_name =  p.contents[0]
            p_link =  p['href'].strip()
            p_price = ''
            price = product.find('span', {'class', 'price'}).find('b')
            # try to find the price inside the <span class='price'><b>$0.00</b></span>
            try:
                p_price = price.text
            # try to find the product if the above doesnt exist
            # <span class='price'> $0.00 </span>
            except:
                p_price = product.find('span', {'class': 'price'}).text
                # insert the data into the database
                self.database.insert(name=p_name, link=p_link, price=p_price)
        # close the database
        self.database.close()

def main(database, url):
    # put database with Product and include the url
    p = Product(database, url)
    # find products and place them in a database
    p.find()