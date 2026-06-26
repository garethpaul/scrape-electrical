# -*- coding: utf-8 -*-
import unittest
try:
    import StringIO
except ImportError:
    import io as StringIO
import os
import sys
import types

import scrape

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from psycopg2.extensions import adapt as psycopg2_adapt
except ImportError:
    psycopg2_adapt = None

try:
    STRING_TYPES = (basestring,)
except NameError:
    STRING_TYPES = (str,)


TITLE_EXTRACTION = "title_text = u' '.join(link.get_text().split())"
HIDDEN_TITLE_CONTENT_REMOVAL = "for hidden_content in link.find_all(['script', 'style']):"


def title_contract_failures(scrape_source, test_source):
    failures = []
    if TITLE_EXTRACTION not in scrape_source:
        failures.append('title extraction must normalize only existing whitespace')
    if HIDDEN_TITLE_CONTENT_REMOVAL not in scrape_source:
        failures.append('title extraction must exclude script and style descendants')
    if 'link.contents[0]' in scrape_source:
        failures.append('title extraction must not use the first anchor child')
    if 'if not title_text:\n            return None' not in scrape_source:
        failures.append('title extraction must skip normalized empty titles')
    if 'return (title_text, link_url, price_text)' not in scrape_source:
        failures.append('database rows must receive normalized plain title text')
    for fixture in ('Nested title', 'ACME Wire Stripper', 'Outlet cover'):
        if fixture in scrape_source:
            failures.append('production title extraction must not hardcode test fixtures')
    for test_name in (
            'test_real_parser_extracts_nested_only_title_as_plain_text',
            'test_real_parser_extracts_complete_mixed_content_title',
            'test_real_parser_preserves_intra_word_and_punctuation_adjacency',
            'test_real_parser_preserves_adjacent_tag_boundaries',
            'test_real_parser_preserves_direct_text_title',
            'test_real_parser_normalizes_whitespace_and_entities',
            'test_available_real_parsers_preserve_title_adjacency',
            'test_real_parser_excludes_script_and_style_text',
            'test_real_parser_skips_truly_empty_title',
            'test_real_parser_title_is_psycopg2_adaptable_without_database',
            'test_real_parser_title_extraction_is_not_fixture_hardcoded'):
        if test_name not in test_source:
            failures.append('missing title extraction regression %s' % test_name)
    return failures


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


class CursorFailingConnection(FakeConnection):
    def __init__(self, close_error=None):
        super(CursorFailingConnection, self).__init__()
        self.close_count = 0
        self.close_error = close_error

    def cursor(self):
        raise RuntimeError('cursor setup failed')

    def close(self):
        self.close_count += 1
        if self.close_error is not None:
            raise self.close_error


class FakeProductDatabase(object):
    def __init__(self):
        self.inserts = []
        self.close_count = 0

    def insert(self, name, link, price):
        self.inserts.append((name, link, price))

    def close(self):
        self.close_count += 1


class FailingCloseProductDatabase(FakeProductDatabase):
    def close(self):
        super(FailingCloseProductDatabase, self).close()
        raise RuntimeError('database close failed')


class FakeHeaders(object):
    def __init__(self, content_encoding=None, content_type=None):
        self.values = {}
        for name, value in (
                ('content-encoding', content_encoding),
                ('content-type', content_type)):
            if isinstance(value, (list, tuple)):
                self.values[name] = list(value)
            elif value is None:
                self.values[name] = []
            else:
                self.values[name] = [value]

    def get(self, name, default=None):
        values = self.values.get(name.lower(), [])
        if values:
            return values[0]
        return default

    def get_all(self, name, default=None):
        return list(self.values.get(name.lower(), default or []))

    def getheaders(self, name):
        return self.get_all(name, [])


class LegacyFakeHeaders(object):
    def __init__(self, content_encoding=None, content_type=None):
        self.headers = FakeHeaders(content_encoding, content_type)

    def get(self, name, default=None):
        return self.headers.get(name, default)

    def getheaders(self, name):
        return self.headers.get_all(name, [])


class FakeResponse(object):
    def __init__(self, body='response body', error=None, content_encoding=None,
                 content_type=None):
        self.body = body
        self.error = error
        self.headers = FakeHeaders(content_encoding, content_type)
        self.closed = False
        self.read_sizes = []
        self.offset = 0

    def info(self):
        return self.headers

    def read(self, size=None):
        self.read_sizes.append(size)
        if self.error is not None:
            raise self.error
        if size is None:
            chunk = self.body[self.offset:]
            self.offset = len(self.body)
            return chunk
        chunk = self.body[self.offset:self.offset + size]
        self.offset += len(chunk)
        return chunk

    def close(self):
        self.closed = True


class FakeRedirectResponse(object):
    def __init__(self):
        self.close_count = 0

    def read(self, size=None):
        return ''

    def readline(self, size=None):
        return ''

    def readlines(self, hint=None):
        return []

    def close(self):
        self.close_count += 1


class ChunkedResponse(object):
    def __init__(self, chunks, content_encoding=None, content_type=None):
        self.chunks = list(chunks)
        self.empty = chunks[0][:0] if chunks else ''
        self.headers = FakeHeaders(content_encoding, content_type)
        self.closed = False
        self.read_sizes = []

    def info(self):
        return self.headers

    def read(self, size=None):
        self.read_sizes.append(size)
        if not self.chunks:
            return self.empty
        chunk = self.chunks.pop(0)
        if size is not None and len(chunk) > size:
            self.chunks.insert(0, chunk[size:])
            return chunk[:size]
        return chunk

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

    def get_text(self, separator='', strip=False):
        text = separator.join(self.contents)
        return text.strip() if strip else text

    def find_all(self, tags):
        return []


class SemanticAnchor(FakeAnchor):
    def __init__(self, text_nodes, href='/item'):
        super(SemanticAnchor, self).__init__(object(), href)
        self.text_nodes = text_nodes

    def get_text(self, separator='', strip=False):
        text_nodes = self.text_nodes
        if strip:
            text_nodes = [text.strip() for text in text_nodes if text.strip()]
        return separator.join(text_nodes)


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


class SemanticProductNode(FakeProductNode):
    def __init__(self, text_nodes):
        super(SemanticProductNode, self).__init__(price_text='$4.00')
        self.title = FakeTitle(SemanticAnchor(text_nodes))


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


def portable_title_behavior_failures(product_class):
    database = FakeProductDatabase()
    product = product_class(database, 'https://example.test/source')
    page = FakePage([
        SemanticProductNode(['Nested title']),
        SemanticProductNode(['ACME ', 'Wire', ' Stripper']),
        SemanticProductNode(['i', 'Phone', ' 15']),
        SemanticProductNode(['ACME', u'®']),
        SemanticProductNode(['ACME', 'Wire', 'Stripper']),
        SemanticProductNode([u'  ACME\xa0', 'Wire\n\tStripper  ']),
        SemanticProductNode([' ', u'\xa0', '\n\t']),
        SemanticProductNode(['Variable ', 'Catalog', ' Entry']),
    ])
    try:
        product.find_products(page)
    except BaseException as error:
        return ['title extraction raised %s' % error.__class__.__name__]

    expected = [
        ('Nested title', 'https://example.test/item', '$4.00'),
        ('ACME Wire Stripper', 'https://example.test/item', '$4.00'),
        ('iPhone 15', 'https://example.test/item', '$4.00'),
        (u'ACME®', 'https://example.test/item', '$4.00'),
        ('ACMEWireStripper', 'https://example.test/item', '$4.00'),
        ('ACME Wire Stripper', 'https://example.test/item', '$4.00'),
        ('Variable Catalog Entry', 'https://example.test/item', '$4.00'),
    ]
    if database.inserts != expected:
        return ['unexpected title rows: %r' % (database.inserts,)]
    for title, unused_link, unused_price in database.inserts:
        if not isinstance(title, STRING_TYPES):
            return ['title is not a plain string: %r' % (title,)]
    return []


class TitleExtractionContractTests(unittest.TestCase):
    def sources(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, 'scrape.py'), 'r') as source_file:
            scrape_source = source_file.read()
        with open(__file__, 'r') as test_file:
            test_source = test_file.read()
        return scrape_source, test_source

    def test_title_extraction_contract_rejects_hostile_mutations(self):
        scrape_source, test_source = self.sources()
        self.assertEqual([], title_contract_failures(scrape_source, test_source))
        self.assertEqual([], portable_title_behavior_failures(scrape.Product))

        mutations = {
            'first child': scrape_source.replace(
                TITLE_EXTRACTION,
                'title_text = link.contents[0]',
                1,
            ),
            'truncated first word': scrape_source.replace(
                TITLE_EXTRACTION,
                "title_text = link.get_text().split()[0]",
                1,
            ),
            'injected node boundaries': scrape_source.replace(
                TITLE_EXTRACTION,
                "title_text = u' '.join(link.get_text(u' ', strip=True).split())",
                1,
            ),
            'missing source boundaries': scrape_source.replace(
                TITLE_EXTRACTION,
                "title_text = u''.join(link.get_text().split())",
                1,
            ),
            'tag leakage': scrape_source.replace(
                TITLE_EXTRACTION,
                "title_text = link.find('span')",
                1,
            ),
            'hardcoded fixture': scrape_source.replace(
                TITLE_EXTRACTION,
                "title_text = u'Nested title'",
                1,
            ),
            'empty title accepted': scrape_source.replace(
                'if not title_text:\n            return None\n',
                '',
                1,
            ),
            'raw title returned': scrape_source.replace(
                'return (title_text, link_url, price_text)',
                'return (link.contents[0], link_url, price_text)',
                1,
            ),
        }
        for description, mutated_source in mutations.items():
            self.assertNotEqual(scrape_source, mutated_source, description)
            self.assertTrue(
                title_contract_failures(mutated_source, test_source),
                '%s mutation was accepted' % description,
            )
            namespace = {'__name__': 'mutated_scrape'}
            eval(compile(mutated_source, 'mutated_scrape.py', 'exec'), namespace)
            self.assertTrue(
                portable_title_behavior_failures(namespace['Product']),
                '%s mutation passed portable behavior' % description,
            )


class DatabaseTests(unittest.TestCase):
    def assertCursorConstructionFailureCloses(self, close_error=None):
        connection = CursorFailingConnection(close_error)
        fake_psycopg2 = types.ModuleType('psycopg2')
        fake_psycopg2.connect = lambda **kwargs: connection
        original_psycopg2 = sys.modules.get('psycopg2', MISSING_HREF)
        sys.modules['psycopg2'] = fake_psycopg2
        try:
            try:
                scrape.Database('db', 'user', 'password', 'host', 'products')
            except RuntimeError as error:
                self.assertEqual('cursor setup failed', str(error))
            else:
                self.fail('cursor construction failure must propagate')
        finally:
            if original_psycopg2 is MISSING_HREF:
                del sys.modules['psycopg2']
            else:
                sys.modules['psycopg2'] = original_psycopg2

        self.assertEqual(1, connection.close_count)

    def test_database_connect_uses_keyword_parameters(self):
        calls = []
        credential_value = 'pass word'
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
                credential_value,
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
                'password': credential_value,
                'host': 'db.example.test',
                'dbname': 'products db',
            }],
            calls,
        )
        self.assertIsInstance(database.cur, FakeCursor)

    def test_constructor_closes_connection_when_cursor_creation_fails(self):
        self.assertCursorConstructionFailureCloses()

    def test_constructor_preserves_cursor_failure_when_connection_close_fails(self):
        self.assertCursorConstructionFailureCloses(RuntimeError('connection close failed'))

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
    def assertConstructionFailureCloses(self, url, **options):
        database = FakeProductDatabase()

        self.assertRaises(ValueError, scrape.main, database, url, **options)
        self.assertEqual(1, database.close_count)

    def test_main_closes_database_when_source_url_validation_fails(self):
        self.assertConstructionFailureCloses('file:///etc/passwd')

    def test_main_closes_database_when_timeout_validation_fails(self):
        self.assertConstructionFailureCloses(
            'https://example.test/source',
            timeout=0,
        )

    def test_main_closes_database_when_response_limit_validation_fails(self):
        self.assertConstructionFailureCloses(
            'https://example.test/source',
            max_response_bytes=0,
        )

    def test_main_leaves_successful_cleanup_to_product_find(self):
        database = FakeProductDatabase()
        original_product = scrape.Product

        class SuccessfulProduct(object):
            def __init__(self, product_database, url, timeout, max_response_bytes):
                self.database = product_database

            def find(self):
                self.database.close()

        scrape.Product = SuccessfulProduct
        try:
            scrape.main(database, 'https://example.test/source')
        finally:
            scrape.Product = original_product

        self.assertEqual(1, database.close_count)

    def assertProductConstructionErrorPreserved(self, primary_error):
        database = FailingCloseProductDatabase()
        original_product = scrape.Product

        class FailingProduct(object):
            def __init__(self, product_database, url, timeout, max_response_bytes):
                raise primary_error

        scrape.Product = FailingProduct
        caught_error = None
        try:
            scrape.main(database, 'https://example.test/source')
        except BaseException as error:
            caught_error = error
        finally:
            scrape.Product = original_product

        self.assertTrue(caught_error is primary_error)
        self.assertEqual(1, database.close_count)

    def test_main_preserves_validation_error_when_cleanup_fails(self):
        self.assertProductConstructionErrorPreserved(ValueError('invalid product configuration'))

    def test_main_closes_database_and_preserves_interruption(self):
        self.assertProductConstructionErrorPreserved(KeyboardInterrupt())

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

    def test_redirect_handler_closes_rejected_response_body(self):
        handler = scrape.SameHostRedirectHandler('https://example.test/source')
        request = scrape.urllib2.Request('https://example.test/source')
        redirect_response = FakeRedirectResponse()

        try:
            handler.redirect_request(
                request,
                redirect_response,
                302,
                'Found',
                {},
                'https://other.test/private',
            )
        except scrape.urllib2.HTTPError:
            self.assertEqual(1, redirect_response.close_count)
        else:
            self.fail('expected redirect rejection')

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
        self.assertEqual('identity', request.get_header('Accept-encoding'))
        self.assertEqual(12, timeout)
        self.assertEqual(
            [
                scrape.DEFAULT_MAX_RESPONSE_BYTES + 1,
                scrape.DEFAULT_MAX_RESPONSE_BYTES - len('response body') + 1,
            ],
            opener.response.read_sizes,
        )
        self.assertTrue(opener.response.closed)

    def test_build_request_requires_identity_content_encoding(self):
        product = scrape.Product(None, 'https://example.test/source')

        request = product.build_request()

        self.assertEqual('identity', request.get_header('Accept-encoding'))

    def test_build_request_accepts_html_source_types(self):
        product = scrape.Product(None, 'https://example.test/source')

        request = product.build_request()

        self.assertEqual(
            'text/html, application/xhtml+xml',
            request.get_header('Accept'),
        )

    def test_read_accepts_identity_content_encoding_variants(self):
        original_build_opener = scrape.urllib2.build_opener
        try:
            for headers_type, content_encoding in (
                    (FakeHeaders, None),
                    (FakeHeaders, ''),
                    (FakeHeaders, ' Identity '),
                    (FakeHeaders, 'identity, IDENTITY'),
                    (FakeHeaders, ['identity', ' Identity ']),
                    (LegacyFakeHeaders, 'identity')):
                response = FakeResponse(content_encoding=content_encoding)
                response.headers = headers_type(content_encoding)
                opener = FakeOpener(response=response)
                scrape.urllib2.build_opener = lambda *args: opener
                product = scrape.Product(None, 'https://example.test/source')

                self.assertEqual('response body', product.read())
                self.assertTrue(response.closed)
        finally:
            scrape.urllib2.build_opener = original_build_opener

    def test_read_rejects_compressed_response_before_body_read(self):
        original_build_opener = scrape.urllib2.build_opener
        try:
            for headers_type, content_encoding in (
                    (FakeHeaders, 'gzip'),
                    (FakeHeaders, 'identity, gzip'),
                    (FakeHeaders, ['identity', 'gzip']),
                    (LegacyFakeHeaders, ['identity', 'gzip'])):
                response = FakeResponse(content_encoding=content_encoding)
                response.headers = headers_type(content_encoding)
                opener = FakeOpener(response=response)
                scrape.urllib2.build_opener = lambda *args: opener
                product = scrape.Product(None, 'https://example.test/source')
                try:
                    product.read()
                except ValueError as error:
                    self.assertEqual('response content encoding must be identity', str(error))
                    self.assertNotIn('gzip', str(error))
                else:
                    self.fail('expected compressed response rejection')

                self.assertEqual([], response.read_sizes)
                self.assertTrue(response.closed)
        finally:
            scrape.urllib2.build_opener = original_build_opener

    def test_read_accepts_html_content_type_variants(self):
        original_build_opener = scrape.urllib2.build_opener
        try:
            for headers_type, content_type in (
                    (FakeHeaders, None),
                    (FakeHeaders, ''),
                    (FakeHeaders, 'text/html'),
                    (FakeHeaders, ' Text/HTML ; charset=UTF-8'),
                    (FakeHeaders, 'APPLICATION/XHTML+XML'),
                    (LegacyFakeHeaders, 'text/html; charset=utf-8')):
                response = FakeResponse(content_type=content_type)
                response.headers = headers_type(None, content_type)
                opener = FakeOpener(response=response)
                scrape.urllib2.build_opener = lambda *args: opener

                product = scrape.Product(None, 'https://example.test/source')
                self.assertEqual('response body', product.read())
                self.assertTrue(response.closed)
        finally:
            scrape.urllib2.build_opener = original_build_opener

    def test_read_rejects_non_html_content_type_before_body_read(self):
        original_build_opener = scrape.urllib2.build_opener
        try:
            for headers_type, content_type in (
                    (FakeHeaders, 'application/json'),
                    (FakeHeaders, 'text/plain; charset=utf-8'),
                    (FakeHeaders, 'image/png'),
                    (FakeHeaders, ['text/html', 'application/json']),
                    (LegacyFakeHeaders, 'application/octet-stream')):
                response = FakeResponse(content_type=content_type)
                response.headers = headers_type(None, content_type)
                opener = FakeOpener(response=response)
                scrape.urllib2.build_opener = lambda *args: opener

                product = scrape.Product(None, 'https://example.test/source')
                try:
                    product.read()
                except ValueError as error:
                    self.assertEqual(
                        'response content type must be HTML',
                        str(error),
                    )
                else:
                    self.fail('expected non-HTML content type rejection')
                self.assertEqual([], response.read_sizes)
                self.assertTrue(response.closed)
        finally:
            scrape.urllib2.build_opener = original_build_opener

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

        self.assertEqual([5, 1], response.read_sizes)
        self.assertTrue(response.closed)

    def test_read_collects_fragmented_body_until_eof(self):
        response = ChunkedResponse([b'ab', b'cd'])
        opener = FakeOpener(response=response)
        original_build_opener = scrape.urllib2.build_opener
        scrape.urllib2.build_opener = lambda *args: opener

        try:
            product = scrape.Product(
                None,
                'https://example.test/source',
                max_response_bytes=4,
            )
            self.assertEqual(b'abcd', product.read())
        finally:
            scrape.urllib2.build_opener = original_build_opener

        self.assertEqual([5, 3, 1], response.read_sizes)
        self.assertTrue(response.closed)

    def test_read_rejects_fragmented_body_over_configured_limit(self):
        response = ChunkedResponse([b'ab', b'cd', b'e'])
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

        self.assertEqual([5, 3, 1], response.read_sizes)
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

    def test_product_rejects_non_string_source_urls_without_echoing_them(self):
        for source_url in [None, True, 1, [], object()]:
            try:
                scrape.Product(None, source_url)
            except ValueError as error:
                self.assertEqual(
                    'source URL must use http or https and include a host',
                    str(error),
                )
                self.assertNotIn(repr(source_url), str(error))
            else:
                self.fail('expected non-string source URL rejection')

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

    def real_product_page(self, anchor_html, parser='html.parser'):
        html = '''
            <div class="zg_item_normal">
              <div class="zg_title"><a href="/item">%s</a></div>
              <span class="price">$4.00</span>
            </div>
        ''' % anchor_html
        return BeautifulSoup(html, parser)

    def parsed_real_title(self, anchor_html, parser='html.parser'):
        database = FakeProductDatabase()
        product = scrape.Product(database, 'https://example.test/source')
        product.find_products(self.real_product_page(anchor_html, parser))
        return database.inserts

    def available_real_parsers(self):
        parsers = []
        for parser in ('html.parser', 'lxml', 'html5lib'):
            try:
                BeautifulSoup('<a>title</a>', parser)
            except Exception:
                continue
            parsers.append(parser)
        return parsers

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_real_parser_extracts_nested_only_title_as_plain_text(self):
        inserts = self.parsed_real_title('<span>Nested title</span>')

        self.assertEqual(1, len(inserts))
        self.assertEqual('Nested title', inserts[0][0])
        self.assertTrue(isinstance(inserts[0][0], STRING_TYPES))

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_real_parser_extracts_complete_mixed_content_title(self):
        inserts = self.parsed_real_title('ACME <span>Wire</span> Stripper')

        self.assertEqual('ACME Wire Stripper', inserts[0][0])

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_real_parser_preserves_intra_word_and_punctuation_adjacency(self):
        self.assertEqual(
            'iPhone 15',
            self.parsed_real_title('i<span>Phone</span> 15')[0][0],
        )
        self.assertEqual(
            u'ACME®',
            self.parsed_real_title('ACME<span>®</span>')[0][0],
        )

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_real_parser_preserves_adjacent_tag_boundaries(self):
        self.assertEqual(
            'ACMEWireStripper',
            self.parsed_real_title('<span>ACME</span><span>Wire</span><span>Stripper</span>')[0][0],
        )
        self.assertEqual(
            'ACME Wire Stripper',
            self.parsed_real_title(
                '<span>ACME</span> <span>Wire</span> <span>Stripper</span>'
            )[0][0],
        )

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_real_parser_preserves_direct_text_title(self):
        inserts = self.parsed_real_title('Outlet cover')

        self.assertEqual('Outlet cover', inserts[0][0])

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_real_parser_normalizes_whitespace_and_entities(self):
        inserts = self.parsed_real_title(
            '  ACME&nbsp; <span> Wire\n\t&amp;\tStripper </span>  '
        )

        self.assertEqual('ACME Wire & Stripper', inserts[0][0])

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_available_real_parsers_preserve_title_adjacency(self):
        parsers = self.available_real_parsers()
        self.assertIn('html.parser', parsers)
        for parser in parsers:
            self.assertEqual(
                'iPhone 15',
                self.parsed_real_title('i<span>Phone</span> 15', parser)[0][0],
                parser,
            )
            self.assertEqual(
                'ACME Wire Stripper',
                self.parsed_real_title('ACME <span>Wire</span> Stripper', parser)[0][0],
                parser,
            )

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_real_parser_excludes_script_and_style_text(self):
        for parser in self.available_real_parsers():
            inserts = self.parsed_real_title(
                'ACME<script>ignored()</script><style>.ignored{}</style><span>®</span>',
                parser,
            )

            self.assertEqual(u'ACME®', inserts[0][0], parser)

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_real_parser_skips_truly_empty_title(self):
        inserts = self.parsed_real_title(' &nbsp; <span>\n\t</span> ')

        self.assertEqual([], inserts)

    @unittest.skipUnless(
        BeautifulSoup is not None and psycopg2_adapt is not None,
        'BeautifulSoup or psycopg2 is unavailable',
    )
    def test_real_parser_title_is_psycopg2_adaptable_without_database(self):
        inserts = self.parsed_real_title('<span>Nested title</span>')

        quoted = psycopg2_adapt(inserts[0][0]).getquoted()

        self.assertTrue(quoted)
        self.assertTrue(isinstance(inserts[0][0], STRING_TYPES))

    @unittest.skipUnless(BeautifulSoup is not None, 'BeautifulSoup is unavailable')
    def test_real_parser_title_extraction_is_not_fixture_hardcoded(self):
        words = ['Variable', 'Catalog', 'Entry']
        anchor_html = '%s <em>%s</em> %s' % tuple(words)

        inserts = self.parsed_real_title(anchor_html)

        self.assertEqual(' '.join(words), inserts[0][0])

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

    def test_normalized_link_rejects_non_string_values(self):
        product = scrape.Product(None, 'https://example.test/source')

        for href in [None, True, 1, [], object()]:
            self.assertIsNone(product.normalized_link(href))

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
