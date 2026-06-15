import unittest
try:
    import StringIO
except ImportError:
    import io as StringIO
import sys
import types

import scrape


MISSING_HREF = object()


class FakeCursor(object):
    def __init__(self):
        self.calls = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params))


class ClosingCursor(FakeCursor):
    def __init__(self, close_order):
        super(ClosingCursor, self).__init__()
        self.close_order = close_order

    def close(self):
        self.close_order.append('cursor')


class FailingClosingCursor(ClosingCursor):
    def close(self):
        super(FailingClosingCursor, self).close()
        raise RuntimeError('cursor close failed')


class FakeConnection(object):
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1


class ClosingConnection(FakeConnection):
    def __init__(self, close_order):
        super(ClosingConnection, self).__init__()
        self.close_order = close_order

    def close(self):
        self.close_order.append('connection')


class FakeDatabaseConnection(FakeConnection):
    def __init__(self):
        super(FakeDatabaseConnection, self).__init__()
        self.cursor_instance = FakeCursor()

    def cursor(self):
        return self.cursor_instance


class FakeProductDatabase(object):
    def __init__(self):
        self.inserts = []

    def insert(self, name, link, price):
        self.inserts.append((name, link, price))


class FakeResponse(object):
    def __init__(self, body='response body', error=None):
        self.body = body
        self.error = error
        self.closed = False
        self.read_sizes = []

    def read(self, size=None):
        self.read_sizes.append(size)
        if self.error is not None:
            raise self.error
        return self.body

    def close(self):
        self.closed = True


class FakeOpener(object):
    def __init__(self, response=None):
        self.calls = []
        self.response = response if response is not None else FakeResponse()

    def open(self, request, timeout=None):
        self.calls.append((request, timeout))
        return self.response


class FakeAnchor(object):
    def __init__(self, name, href=MISSING_HREF):
        self.contents = [name]
        self.href = href

    def __getitem__(self, key):
        if key == 'href' and self.href is not MISSING_HREF:
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
    def __init__(self, name=None, href=MISSING_HREF, price_text=None, bold_price=None):
        self.title = None
        self.price = None
        if name is not None:
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
    def test_database_connect_uses_keyword_parameters(self):
        calls = []
        fake_psycopg2 = types.ModuleType('psycopg2')

        def connect(**kwargs):
            calls.append(kwargs)
            return FakeDatabaseConnection()

        fake_psycopg2.connect = connect
        original_psycopg2 = sys.modules.get('psycopg2', MISSING_HREF)
        sys.modules['psycopg2'] = fake_psycopg2
        try:
            database = scrape.Database(
                'products db',
                'scraper user',
                'pass word',
                'db.example.test',
                'products'
            )
        finally:
            if original_psycopg2 is MISSING_HREF:
                del sys.modules['psycopg2']
            else:
                sys.modules['psycopg2'] = original_psycopg2

        self.assertEqual(
            [{
                'user': 'scraper user',
                'password': 'pass word',
                'host': 'db.example.test',
                'dbname': 'products db',
            }],
            calls,
        )
        self.assertIsInstance(database.cur, FakeCursor)

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

    def test_close_closes_cursor_before_connection(self):
        close_order = []
        database = database_with('products')
        database.cur = ClosingCursor(close_order)
        database.conn = ClosingConnection(close_order)

        database.close()

        self.assertEqual(['cursor', 'connection'], close_order)

    def test_close_closes_connection_when_cursor_close_fails(self):
        close_order = []
        database = database_with('products')
        database.cur = FailingClosingCursor(close_order)
        database.conn = ClosingConnection(close_order)

        self.assertRaises(RuntimeError, database.close)

        self.assertEqual(['cursor', 'connection'], close_order)


class CLITests(unittest.TestCase):
    def test_parse_args_supports_dry_run_without_database_credentials(self):
        options = scrape.parse_args([
            '--url', 'https://example.test/source',
            '--dry-run',
            '--timeout', '7',
            '--max-response-bytes', '4096',
        ])

        self.assertEqual('https://example.test/source', options.url)
        self.assertTrue(options.dry_run)
        self.assertEqual(7.0, options.timeout)
        self.assertEqual(4096, options.max_response_bytes)

    def test_run_cli_forwards_response_limit(self):
        calls = []
        original_database_from_options = scrape.database_from_options
        original_main = scrape.main
        scrape.database_from_options = lambda options: 'database'
        scrape.main = lambda database, url, timeout, max_response_bytes: calls.append(
            (database, url, timeout, max_response_bytes)
        )
        try:
            scrape.run_cli([
                '--url', 'https://example.test/source',
                '--dry-run',
                '--timeout', '9',
                '--max-response-bytes', '2048',
            ])
        finally:
            scrape.database_from_options = original_database_from_options
            scrape.main = original_main

        self.assertEqual(
            [('database', 'https://example.test/source', 9.0, 2048)],
            calls,
        )

    def test_dry_run_database_prints_parsed_rows_without_closing_resources(self):
        output = StringIO.StringIO()
        database = scrape.DryRunDatabase(output=output)

        database.insert('Wire stripper', 'https://example.test/item', '$8.50')
        database.close()

        self.assertEqual(
            'Wire stripper\thttps://example.test/item\t$8.50\n',
            output.getvalue(),
        )

    def test_database_from_options_uses_dry_run_database_without_credentials(self):
        options = scrape.parse_args([
            '--url', 'https://example.test/source',
            '--dry-run',
        ])

        database = scrape.database_from_options(options)

        self.assertIsInstance(database, scrape.DryRunDatabase)

    def test_database_from_options_requires_live_database_credentials(self):
        options = scrape.parse_args(['--url', 'https://example.test/source'])

        try:
            scrape.database_from_options(options)
            self.fail('database_from_options should reject missing live database credentials')
        except ValueError as error:
            message = str(error)

        self.assertIn('--db-name', message)
        self.assertIn('--db-user', message)
        self.assertIn('--db-password', message)
        self.assertIn('--db-host', message)

    def test_database_from_options_builds_database_for_live_run(self):
        calls = []

        def fake_database(db_name, db_user, db_password, db_host, table_name):
            calls.append((db_name, db_user, db_password, db_host, table_name))
            return 'database'

        original_database = scrape.Database
        scrape.Database = fake_database
        try:
            options = scrape.parse_args([
                '--url', 'https://example.test/source',
                '--db-name', 'products_db',
                '--db-user', 'scraper',
                '--db-password', 'secret',
                '--db-host', 'db.example.test',
                '--table-name', 'electrical_products',
            ])

            database = scrape.database_from_options(options)
        finally:
            scrape.Database = original_database

        self.assertEqual('database', database)
        self.assertEqual(
            [('products_db', 'scraper', 'secret', 'db.example.test', 'electrical_products')],
            calls,
        )


class ProductParserTests(unittest.TestCase):
    def redirect_request(self, source_url, current_url, redirect_url):
        handler = scrape.SameHostRedirectHandler(source_url)
        request = scrape.urllib2.Request(current_url)
        return handler.redirect_request(
            request, None, 302, 'Found', {}, redirect_url
        )

    def test_redirect_handler_has_explicit_hop_limits(self):
        handler = scrape.SameHostRedirectHandler('https://example.test/source')

        self.assertEqual(2, handler.max_repeats)
        self.assertEqual(5, handler.max_redirections)

    def test_redirect_handler_allows_same_host_relative_redirect(self):
        request = self.redirect_request(
            'https://example.test/source',
            'https://example.test/source',
            '/next?page=2',
        )

        self.assertEqual('https://example.test/next?page=2', request.get_full_url())

    def test_redirect_handler_allows_same_host_https_upgrade(self):
        request = self.redirect_request(
            'http://example.test/source',
            'http://example.test/source',
            'https://EXAMPLE.test/secure',
        )

        self.assertEqual('https://EXAMPLE.test/secure', request.get_full_url())

    def test_redirect_handler_rejects_unsafe_targets_without_echoing_them(self):
        unsafe_targets = [
            'https://other.test/private',
            '//other.test/private',
            'http://example.test/insecure',
            'https://example.test:8443/private',
            'file:///etc/passwd',
            'https:///missing-host',
            'http://[invalid-ipv6',
            'http://:80/missing-hostname',
            'https://user:secret@example.test/private',
        ]

        for redirect_url in unsafe_targets:
            try:
                self.redirect_request(
                    'https://example.test/source',
                    'https://example.test/source',
                    redirect_url,
                )
            except scrape.urllib2.HTTPError as error:
                self.assertEqual('redirect target violates same-host policy', error.msg)
                self.assertEqual('https://example.test/', error.filename)
                self.assertNotIn(redirect_url, str(error))
            else:
                self.fail('expected redirect rejection for %r' % redirect_url)

    def test_read_uses_bounded_timeout(self):
        opener = FakeOpener()
        original_build_opener = scrape.urllib2.build_opener
        handlers = []
        scrape.urllib2.build_opener = lambda *args: handlers.extend(args) or opener

        try:
            product = scrape.Product(None, 'https://example.test/source', timeout=12)
            self.assertEqual('response body', product.read())
        finally:
            scrape.urllib2.build_opener = original_build_opener

        self.assertEqual(1, len(opener.calls))
        self.assertEqual(1, len(handlers))
        self.assertIsInstance(handlers[0], scrape.SameHostRedirectHandler)
        request, timeout = opener.calls[0]
        self.assertEqual('https://example.test/source', request.get_full_url())
        self.assertEqual(12, timeout)
        self.assertEqual(
            [scrape.DEFAULT_MAX_RESPONSE_BYTES + 1],
            opener.response.read_sizes,
        )
        self.assertTrue(opener.response.closed)

    def test_read_accepts_body_at_configured_limit(self):
        response = FakeResponse(body='1234')
        opener = FakeOpener(response=response)
        original_build_opener = scrape.urllib2.build_opener
        scrape.urllib2.build_opener = lambda *args: opener

        try:
            product = scrape.Product(
                None,
                'https://example.test/source',
                max_response_bytes=4,
            )
            self.assertEqual('1234', product.read())
        finally:
            scrape.urllib2.build_opener = original_build_opener

        self.assertEqual([5], response.read_sizes)
        self.assertTrue(response.closed)

    def test_read_rejects_and_closes_oversized_body(self):
        response = FakeResponse(body='12345')
        opener = FakeOpener(response=response)
        original_build_opener = scrape.urllib2.build_opener
        scrape.urllib2.build_opener = lambda *args: opener

        try:
            product = scrape.Product(
                None,
                'https://example.test/source',
                max_response_bytes=4,
            )
            self.assertRaises(ValueError, product.read)
        finally:
            scrape.urllib2.build_opener = original_build_opener

        self.assertEqual([5], response.read_sizes)
        self.assertTrue(response.closed)

    def test_read_closes_response_when_body_read_fails(self):
        response = FakeResponse(error=RuntimeError('read failed'))
        opener = FakeOpener(response=response)
        original_build_opener = scrape.urllib2.build_opener
        scrape.urllib2.build_opener = lambda *args: opener

        try:
            product = scrape.Product(None, 'https://example.test/source')
            self.assertRaises(RuntimeError, product.read)
        finally:
            scrape.urllib2.build_opener = original_build_opener

        self.assertTrue(response.closed)

    def test_product_accepts_positive_finite_timeout(self):
        for value in [1, 0.5, 30]:
            product = scrape.Product(None, 'https://example.test/source', timeout=value)
            self.assertEqual(value, product.timeout)

    def test_product_rejects_invalid_timeout_values(self):
        for value in [True, '1', None, 0, -1, float('nan'), float('inf'), float('-inf')]:
            self.assertRaises(
                ValueError,
                scrape.Product,
                None,
                'https://example.test/source',
                timeout=value,
            )

    def test_product_rejects_non_positive_response_limit(self):
        self.assertRaises(
            ValueError,
            scrape.Product,
            None,
            'https://example.test/source',
            max_response_bytes=0,
        )

    def test_product_rejects_non_integer_response_limit(self):
        for value in [True, 1.5, '4']:
            self.assertRaises(
                ValueError,
                scrape.Product,
                None,
                'https://example.test/source',
                max_response_bytes=value,
            )

    def test_product_rejects_non_web_source_urls(self):
        for source_url in [
            '',
            '   ',
            'file:///etc/passwd',
            'javascript:alert(1)',
            'example.test/source',
            'https:///missing-host',
            'http://[invalid-ipv6',
        ]:
            self.assertRaises(ValueError, scrape.Product, None, source_url)

    def test_product_rejects_malformed_source_authorities_without_echoing_them(self):
        for source_url in [
            'http://example.test:not-a-port/source',
            'http://example.test:/source',
            'http://example.test:65536/source',
            'http://[invalid-ipv6/source',
            'http://::1/source',
        ]:
            try:
                scrape.Product(None, source_url)
            except ValueError as error:
                self.assertEqual(
                    'source URL must use http or https and include a host',
                    str(error),
                )
                self.assertNotIn(source_url, str(error))
            else:
                self.fail('expected malformed source authority rejection')

        for source_url in [
            'https://example.test:8443/source',
            'http://[::1]:8080/source',
        ]:
            product = scrape.Product(None, source_url)
            self.assertEqual(source_url, product.url)

    def test_product_strips_source_url_whitespace(self):
        product = scrape.Product(None, ' https://example.test/source ')

        self.assertEqual('https://example.test/source', product.url)

    def test_product_rejects_source_url_credentials_without_echoing_them(self):
        for source_url in [
            'https://operator@example.test/source',
            'https://:password@example.test/source',
            'https://user%40name:pass%2Fword@example.test/source',
        ]:
            try:
                scrape.Product(None, source_url)
            except ValueError as error:
                self.assertEqual('source URL must not include credentials', str(error))
                self.assertNotIn(source_url, str(error))
            else:
                self.fail('expected source credential rejection')

    def test_build_request_uses_plain_url_without_spoofing_headers(self):
        product = scrape.Product(None, 'https://example.test/source')

        request = product.build_request()

        self.assertEqual('https://example.test/source', request.get_full_url())
        self.assertNotIn('User-agent', request.headers)
        self.assertNotIn('Referer', request.headers)
        self.assertNotIn('Dnt', request.headers)

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
            FakeProductNode('Missing href', price_text='$4.00'),
            FakeProductNode('Blank href', '', '$5.00'),
            FakeProductNode(price_text='$3.00'),
        ])

        product.find_products(page)

        self.assertEqual([], database.inserts)

    def test_find_products_skips_non_web_links(self):
        database = FakeProductDatabase()
        product = scrape.Product(database, 'https://example.test/source')
        page = FakePage([
            FakeProductNode('Script link', 'javascript:alert(1)', '$1.00'),
            FakeProductNode('Local file', 'file:///etc/passwd', '$2.00'),
            FakeProductNode('Mail link', 'mailto:sales@example.test', '$3.00'),
            FakeProductNode('Valid item', 'https://example.test/item', '$4.00'),
        ])

        product.find_products(page)

        self.assertEqual(
            [('Valid item', 'https://example.test/item', '$4.00')],
            database.inserts,
        )

    def test_find_products_skips_credential_bearing_links(self):
        database = FakeProductDatabase()
        product = scrape.Product(database, 'https://example.test/source')
        page = FakePage([
            FakeProductNode('Username', 'https://operator@example.test/item', '$1.00'),
            FakeProductNode('Password', 'https://:secret@example.test/item', '$2.00'),
            FakeProductNode('Encoded', 'https://user%40name:pass%2Fword@example.test/item', '$3.00'),
            FakeProductNode('Valid item', 'https://example.test/item', '$4.00'),
        ])

        product.find_products(page)

        self.assertEqual(
            [('Valid item', 'https://example.test/item', '$4.00')],
            database.inserts,
        )

    def test_find_products_skips_malformed_links_and_continues(self):
        database = FakeProductDatabase()
        product = scrape.Product(database, 'https://example.test/source')
        page = FakePage([
            FakeProductNode('Invalid IPv6', 'https://[invalid/item', '$1.00'),
            FakeProductNode('Invalid port', 'https://example.test:not-a-port/item', '$2.00'),
            FakeProductNode('Valid item', '/item/123', '$3.00'),
        ])

        product.find_products(page)

        self.assertEqual(
            [('Valid item', 'https://example.test/item/123', '$3.00')],
            database.inserts,
        )

    def test_find_products_normalizes_relative_links(self):
        database = FakeProductDatabase()
        product = scrape.Product(database, 'https://example.test/source/list')
        page = FakePage([
            FakeProductNode('Relative item', '/item/123', '$4.00'),
        ])

        product.find_products(page)

        self.assertEqual(
            [('Relative item', 'https://example.test/item/123', '$4.00')],
            database.inserts,
        )


if __name__ == '__main__':
    unittest.main()
