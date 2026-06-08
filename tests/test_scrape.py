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


if __name__ == '__main__':
    unittest.main()
