import requests


class MountebankException(Exception):
    pass


class Microservice:
    def __init__(self, definition, mountebank):
        resp = mountebank.create_imposter(definition)
        if resp.status_code != 201:
            raise MountebankException("{}: {}".format(resp.status_code, resp.text))
        self.port = resp.json()['port']
        self.mountebank = mountebank

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def _get_self(self):
        return self.mountebank.get_imposter(self.port)

    @property
    def requests(self):
        return self._get_self().json()['requests']

    def url(self, path):
        return u'{}:{}{}'.format(self.mountebank.host, self.port, path)

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
            return requests.post(self.imposter_url, json=definition)
        else:
            return requests.post(self.imposter_url, data=definition)

    def reset(self):
        return requests.delete(self.imposter_url)

    def delete_imposter(self, port):
        return requests.delete('{}/{}'.format(self.imposter_url, port))

    def get_all_imposters(self):
        return requests.get(self.imposter_url)

    def get_imposter(self, port):
        return requests.get('{}/{}'.format(self.imposter_url, port)).json()

    def microservice(self, definition):
        return Microservice(definition, self)


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
