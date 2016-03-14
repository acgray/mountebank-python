# mountebank-python

Simple Python library for Mountebank, designed for easy use in integration tests.

Usage:

```python
import mountebank

mb = mountebank.Mountebank()

definition = {"protocol": "http",
              "stubs": [{
                  "responses": [{
                      "is": {"statusCode": 400}}],
                  "predicates": [{
                      "and": [{
                          "equals": {
                              "path": "/account_overview",
                              "method": "POST"}}, {
                          "not": {
                              "exists": {
                                  "query": {
                                      "advertiser": True,
                                      "start_date": True,
                                      "end_date": True}},
                              "caseSensitive": True}}]}]}]}

service = mb.microservice(definition)

assert requests.post(ms.url('/account_overview'), params={'advertiser': 'a', 'start_date': 'b', 'end_date': 'c'}).status_code == 200
assert requests.post(ms.url('/account_overview'), params={'advertiser': 'a', 'start_date': 'b'}).status_code == 400

service.destroy()

# context manager usage

with mb.microservice(definition):
    assert requests.post(ms.url('/account_overview'), params={'advertiser': 'a', 'start_date': 'b', 'end_date': 'c'}).status_code == 200
    assert requests.post(ms.url('/account_overview'), params={'advertiser': 'a', 'start_date': 'b'}).status_code == 400
```