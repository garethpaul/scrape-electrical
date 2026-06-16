from __future__ import print_function

import argparse
import re
import sys

try:
    import urllib2
    from urlparse import urljoin, urlparse
except ImportError:
    import urllib.error
    import urllib.request as urllib2
    from urllib.parse import urljoin, urlparse

    urllib2.HTTPError = urllib.error.HTTPError

try:
    INTEGER_TYPES = (int, long)
except NameError:
    INTEGER_TYPES = (int,)


DEFAULT_MAX_RESPONSE_BYTES = 5 * 1024 * 1024


class SameHostRedirectHandler(urllib2.HTTPRedirectHandler):
    max_repeats = 2
    max_redirections = 5

    def __init__(self, source_url):
        parsed_source = urlparse(source_url)
        self.source_scheme = parsed_source.scheme
        self.source_host = parsed_source.hostname.lower()
        self.source_port = parsed_source.port or self.default_port(self.source_scheme)
        self.safe_source_url = '%s://%s/' % (parsed_source.scheme, self.source_host)

    def default_port(self, scheme):
        return 443 if scheme == 'https' else 80

    def rejected_redirect(self, code, headers, fp):
        return urllib2.HTTPError(
            self.safe_source_url,
            code,
            'redirect target violates same-host policy',
            headers,
            fp
        )

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        try:
            raw_redirect = urlparse(newurl)
            current_scheme = urlparse(req.get_full_url()).scheme
            redirect_url = urljoin(req.get_full_url(), newurl)
            parsed_redirect = urlparse(redirect_url)
            redirect_host = parsed_redirect.hostname
            redirect_port = parsed_redirect.port or self.default_port(parsed_redirect.scheme)
        except ValueError:
            raise self.rejected_redirect(code, headers, fp)

        same_origin = (
            parsed_redirect.scheme == self.source_scheme and
            redirect_port == self.source_port
        )
        standard_https_upgrade = (
            self.source_scheme == 'http' and self.source_port == 80 and
            parsed_redirect.scheme == 'https' and redirect_port == 443
        )
        allowed = (
            not (raw_redirect.scheme and not raw_redirect.netloc) and
            parsed_redirect.scheme in ('http', 'https') and
            not (current_scheme == 'https' and parsed_redirect.scheme == 'http') and
            redirect_host is not None and
            redirect_host.lower() == self.source_host and
            (same_origin or standard_https_upgrade) and
            parsed_redirect.username is None and
            parsed_redirect.password is None
        )
        if not allowed:
            raise self.rejected_redirect(code, headers, fp)

        return urllib2.HTTPRedirectHandler.redirect_request(
            self, req, fp, code, msg, headers, redirect_url
        )


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
    def __init__(self, database, url, timeout=30,
                 max_response_bytes=DEFAULT_MAX_RESPONSE_BYTES):
        # Set variables for class product.
        self.database = database
        self.url = self.normalized_source_url(url)
        if (isinstance(timeout, bool) or
                not isinstance(timeout, INTEGER_TYPES + (float,)) or
                timeout <= 0 or timeout != timeout or
                timeout == float('inf')):
            raise ValueError('timeout must be positive')
        self.timeout = timeout
        if (isinstance(max_response_bytes, bool) or
                not isinstance(max_response_bytes, INTEGER_TYPES) or
                max_response_bytes <= 0):
            raise ValueError('maximum response size must be a positive integer')
        self.max_response_bytes = max_response_bytes

    def normalized_source_url(self, url):
        if not url or not url.strip():
            raise ValueError('source URL must use http or https and include a host')

        source_url = url.strip()
        try:
            parsed_url = urlparse(source_url)
            source_host = parsed_url.hostname
            source_port = parsed_url.port
        except ValueError:
            raise ValueError('source URL must use http or https and include a host')
        source_authority = parsed_url.netloc.rsplit('@', 1)[-1]
        explicit_port = re.search(r'(?:\]|[^:]):([^:]*)$', source_authority)
        if explicit_port is not None and source_port is None:
            raise ValueError('source URL must use http or https and include a host')
        if (parsed_url.scheme not in ('http', 'https') or
                not parsed_url.netloc or not source_host):
            raise ValueError('source URL must use http or https and include a host')
        if parsed_url.username is not None or parsed_url.password is not None:
            raise ValueError('source URL must not include credentials')

        return source_url

    def read(self):
        opener = urllib2.build_opener(SameHostRedirectHandler(self.url))
        response = opener.open(self.build_request(), timeout=self.timeout)
        try:
            headers = response.info()
            for content_encoding in self.header_values(
                    headers, 'Content-Encoding'):
                declared_encodings = content_encoding.split(',')
                if any(encoding.strip().lower() not in ('', 'identity')
                       for encoding in declared_encodings):
                    raise ValueError('response content encoding must be identity')
            for content_type in self.header_values(headers, 'Content-Type'):
                media_type = content_type.split(';', 1)[0].strip().lower()
                if media_type not in ('', 'text/html', 'application/xhtml+xml'):
                    raise ValueError('response content type must be HTML')

            chunks = []
            remaining = self.max_response_bytes + 1
            while remaining > 0:
                chunk = response.read(remaining)
                if not chunk:
                    if not chunks:
                        return chunk
                    break
                if len(chunk) > remaining:
                    chunk = chunk[:remaining]
                chunks.append(chunk)
                remaining -= len(chunk)

            body = chunks[0][:0].join(chunks)
            if len(body) > self.max_response_bytes:
                raise ValueError(
                    'response body exceeds maximum of %d bytes' % self.max_response_bytes
                )
            return body
        finally:
            response.close()

    def header_values(self, headers, name):
        if hasattr(headers, 'get_all'):
            return headers.get_all(name, [])
        if hasattr(headers, 'getheaders'):
            return headers.getheaders(name) or []
        return [headers.get(name) or '']

    def build_request(self):
        request = urllib2.Request(self.url)
        request.add_header('Accept', 'text/html, application/xhtml+xml')
        request.add_header('Accept-Encoding', 'identity')
        return request

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

        try:
            link_url = urljoin(self.url, href.strip())
            parsed_url = urlparse(link_url)
            # These properties reject malformed IPv6 hosts and port values.
            link_host = parsed_url.hostname
            parsed_url.port
        except ValueError:
            return None
        if (parsed_url.scheme not in ('http', 'https') or
                not parsed_url.netloc or link_host is None):
            return None
        if parsed_url.username is not None or parsed_url.password is not None:
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
    parser.add_argument(
        '--max-response-bytes',
        type=int,
        default=DEFAULT_MAX_RESPONSE_BYTES,
        help='maximum source response size in bytes'
    )
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

    main(
        database,
        options.url,
        timeout=options.timeout,
        max_response_bytes=options.max_response_bytes
    )


def main(database, url, timeout=30,
         max_response_bytes=DEFAULT_MAX_RESPONSE_BYTES):
    # put database with Product and include the url
    p = Product(
        database,
        url,
        timeout=timeout,
        max_response_bytes=max_response_bytes
    )
    # find products and place them in a database
    p.find()


if __name__ == '__main__':
    run_cli()
