# Independent research answers - eCommerce Part 1

## Requests

Requests is a Python library for acting as an HTTP client. A program calls
requests.get(url, params=...) to retrieve a resource, or supplies a JSON body
to requests.post(url, json=...) to submit one. Its Response object exposes
status_code, headers, text and json(). Parsing JSON does not establish that
the server accepted the request; raise_for_status() checks error statuses
separately. Every external request should have a timeout and explicit error
handling. Authentication headers and TLS certificate verification protect
transport and identity. Tests can mock the client so they remain independent
of an external service's availability. Our JSONPlaceholder helper applies
these techniques and returns a safe empty result when retrieval fails.

Source: https://requests.readthedocs.io/en/latest/user/quickstart/

## JSON

JSON is a language-independent representation of objects, arrays, strings,
numbers, booleans and null. It is commonly used for web API responses and
configuration. A Python dictionary can be encoded as JSON, but it is not
itself JSON until serialised into the format's textual syntax.

Advantages:
1. Compact structure reduces transfer size compared with verbose tagged data.
2. Arrays and objects map naturally to common programming-language structures.
3. Parsing and generation are supported by many standard libraries.
4. Simple nesting is readable and convenient for APIs.

Disadvantages:
1. No native date, binary or decimal-money type; applications need conventions.
2. No standard comment syntax in ordinary JSON documents.
3. Parsing alone does not validate a business schema or enforce permissions.
4. Deep nesting or oversized documents can consume significant memory and CPU.

Sources: https://www.json.org/json-en.html and https://www.rfc-editor.org/rfc/rfc8259

## XML

XML represents structured documents through named elements, attributes and
text. It is useful for document exchange, publishing and established enterprise
interfaces. Namespaces distinguish vocabularies, and schema systems can express
structural rules. It can represent mixed text and markup more naturally than
a basic object-oriented JSON representation.

Advantages:
1. Mixed content supports richly structured documents.
2. Namespaces allow distinct vocabularies to coexist without name collisions.
3. Established validation tools support formal schema checking.
4. Mature tools such as XPath and XSLT support querying and transformation.

Disadvantages:
1. Repeated tags can make payloads large and verbose.
2. Attributes, elements and namespaces add modelling and parsing complexity.
3. It maps less directly to ordinary dictionaries and arrays than JSON.
4. Unsafe parser configuration can allow entity-expansion or external-entity
   attacks; untrusted XML requires hardened parsing.

Source: https://www.w3.org/XML/

## RESTful APIs

REST describes architectural constraints for distributed systems, rather than
a particular library or a synonym for JSON. Clients interact with resources
identified by URIs through representations and a uniform interface. HTTP APIs
commonly use GET for retrieval, POST for creation, PUT for replacement and
DELETE for removal. Each request carries enough information for processing;
statelessness does not mean the server cannot persist resource data. Responses
use meaningful status codes and, where suitable, caching metadata. Strict REST
also includes hypermedia-driven navigation. APIs connect browser front ends,
mobile apps and independent services without exposing database internals.

Advantages:
1. Client/server separation allows independent implementation and evolution.
2. Standard HTTP mechanisms work with widely available clients and tooling.
3. Stateless request handling simplifies horizontal scaling.
4. Cacheable representations can reduce latency and server load.

Disadvantages:
1. Fixed resource representations can cause over-fetching or extra round trips.
2. Cross-resource operations need careful transaction and consistency design.
3. Versioning and backward compatibility require ongoing discipline.
4. HTTP conventions alone do not provide authorisation, rate limiting or input
   validation; these must be designed and implemented separately.

Sources: https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm
and https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
