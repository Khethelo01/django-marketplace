# Marketplace requirements and design

## Users and workflows

Visitors browse stores and products, then register as a buyer or vendor.
Buyers build a session cart across stores, remove items, place an order,
view their invoice, receive invoice email and write reviews. Vendors create,
read, edit and delete only their own stores and products. Both roles can
authenticate to the API and list vendor stores and each store's products.
Only vendors create stores and only a store's vendor adds its products.
Vendor review retrieval is restricted to reviews on their own products.

## Interface

Home lists stores and products. Store detail lists its catalogue. Product
detail presents description, price, stock, a quantity control and reviews.
Dashboard separates vendor management from buyer invoice history. Every
destructive action uses a confirmation screen and POST with CSRF protection.
Forms keep invalid input and display errors. Layout adapts from three columns
to two and then one. Keyboard focus is visible; controls have text labels.

## Normalised data

User stores authentication, unique email and role. Store references its vendor;
Product references its store. Review references its buyer and product. Order
references its buyer; OrderItem references the order and optional product.
No comma-separated lists or repeating groups are stored. Each relationship
has a foreign key. Invoice name and unit price are intentional historical
snapshots: a later product price change must not rewrite an old invoice.
Verified status is derived from actual OrderItem records, never client input.

## Access and security

Django hashes passwords and supplies login sessions and expiring, single-use
password-reset tokens (15-minute timeout). Role validation uses server-side
form choices. Store/product lookups include their owner; changing a URL cannot
grant access. Invoice queries include the buyer. API ownership is assigned
from request.user; clients cannot select a different vendor. API uses token
or CSRF-protected session authentication. Production requires HTTPS, private
environment secrets, DEBUG=False, restrictive hosts and a configured SMTP
account. The coursework defaults use console mail; no real email is sent.

## Failure and recovery

Checkout recalculates prices from database records, validates quantities,
locks rows and conditionally decrements stock inside a transaction. If stock
is unavailable, all order changes roll back and the cart remains. A successful
order clears the cart. Invoice delivery failure preserves the order and gives
the buyer a retry action. Missing/deleted products produce a useful checkout
message instead of silently dropping items. GET never deletes. Unknown objects
return 404; role violations return 403. External API requests have a timeout,
status checking, JSON validation and a visible fallback. Automated tests cover
successful and unsuccessful permission and integration paths.

## API contract (Part 2)

POST /api/token/ exchanges valid credentials for a token. Send it as
Authorization: Token YOUR_TOKEN. Never commit real tokens.

| Endpoint | Methods | Access |
| --- | --- | --- |
| /api/stores/ | GET | Authenticated buyer/vendor; optional ?vendor=ID |
| /api/stores/ | POST | Vendor; name and optional description |
| /api/stores/ID/products/ | GET | Authenticated buyer/vendor |
| /api/stores/ID/products/ | POST | Store owner; name, description, price, stock |
| /api/reviews/ | GET | Vendor; own store reviews |
| /external-posts/?user_id=1 | GET | HTML integration and optional filtering |

JSON is the representation. Creation returns 201; invalid data 400; missing
authentication 401; role/ownership denial 403; missing records 404. Passwords
and authentication tokens never appear in product, store or review responses.
These are resource-oriented HTTP endpoints; hypermedia navigation is not claimed.
