import requests


class MountebankException(Exception):
    pass


class Microservice:
    def __init__(self, definition, mountebank, host=None):
        resp = mountebank.create_imposter(definition)
        self.port = resp['port']
        self.mountebank = mountebank
        self.host = host or self.mountebank.host

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def _get_self(self):
        return self.mountebank.get_imposter(self.port)

    @property
    def requests(self):
        return self._get_self().json().get('requests', [])

    def url(self, path):
        return u'{}:{}{}'.format(self.host, self.port, path)

    def destroy(self):
        return self.mountebank.delete_imposter(self.port)


class TestContext:
    def __init__(self):
        print "init"

    def __enter__(self):
        print "enter"

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "exit"


class Mountebank:
    def __init__(self, host=u'localhost', port=2525, ssl=False):
        self.host = host
        self.port = port
        self.ssl = ssl

    @property
    def imposter_url(self):
        return '{}://{}:{}/imposters'.format('https' if self.ssl else 'http', self.host, self.port)

    def create_imposter(self, definition):
        if isinstance(definition, dict):
            resp = requests.post(self.imposter_url, json=definition)
        else:
            resp = requests.post(self.imposter_url, data=definition)
        resp.raise_for_status()
        return resp.json()

    def reset(self):
        resp = requests.delete(self.imposter_url)
        resp.raise_for_status()
        return resp.json()

    def delete_imposter(self, port):
        resp = requests.delete('{}/{}'.format(self.imposter_url, port))
        resp.raise_for_status()
        return resp.json()

    def get_all_imposters(self):
        resp = requests.get(self.imposter_url)
        resp.raise_for_status()
        return resp.json()

    def get_imposter(self, port):
        resp = requests.get('{}/{}'.format(self.imposter_url, port))
        resp.raise_for_status()
        return resp.json()

    def microservice(self, definition, host):
        return Microservice(definition, self, host)


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
