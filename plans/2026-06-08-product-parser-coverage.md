# Product Parser Coverage

## Problem

`Product.find()` only inserted rows when the nested `<b>` price lookup failed.
That meant the expected `<span class="price"><b>$0.00</b></span>` shape parsed
a price but skipped the database insert, while the fallback path depended on a
broad `except`.

## TDD Evidence

1. Added Python 2 parser tests with mocked page/product nodes for nested bold
   prices, plain price spans, and incomplete product rows.
2. Split product extraction into `find_products()` and `product_fields()` so the
   parser can be tested without network access or BeautifulSoup installed.
3. Replaced the broad exception fallback with explicit title, link, and price
   checks before inserting parsed products.

## Verification

- `make lint`
- `make test`
- `make verify`
- `git diff --check`
