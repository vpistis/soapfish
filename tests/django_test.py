# encoding: utf-8

from __future__ import absolute_import

from collections import namedtuple
from datetime import datetime as DateTime

try:
    import django
    from django.conf.urls import url
    from django.conf import empty
    from django.test import Client
except (ImportError, SyntaxError):
    # Django 1.8 does not support Python 2.6 anymore, importing the module
    # triggers a SyntaxError which causes builds to fail.
    django = None
from nose import SkipTest
from pythonic_testcase import *

from soapfish.django_ import django_dispatcher
from soapfish.testutil import echo_service
from soapfish.lib.attribute_dict import AttrDict

Urlconf = namedtuple('Urlconf', 'urlpatterns')


class DjangoDispatchTest(PythonicTestCase):
    def setUp(self):
        if django is None:
            raise SkipTest('django not installed')
        super(DjangoDispatchTest, self).setUp()
        self.service = echo_service()
        if django.conf.settings.__dict__['_wrapped'] is empty:
            django.conf.settings.configure(self.django_settings())

            django.conf.settings.update(AttrDict(
                ROOT_URLCONF=Urlconf(
                    urlpatterns=(
                        url(r"^ws/$", django_dispatcher(self.service)),
                    )
                ),
            ))
        django.setup()
        self.client = Client()

    def test_can_retrieve_wsdl_via_django(self):
        response = self.client.get('/ws/', {'wsdl': None})
        assert_equals(200, response.status_code)
        assert_equals('text/xml', response.get('Content-Type'))
        assert_contains('<wsdl:definitions', response.content.decode('utf8'))

    def test_can_dispatch_simple_request_through_django(self):
        input_value = str(DateTime.now())
        headers, body = self._soap_request(input_value)
        response = self.client.post('/ws/', body, **headers)
        assert_equals(200, response.status_code)
        body = self._parse_soap_response(response.content)
        assert_equals(input_value, body.value)

    # --- internal helpers ----------------------------------------------------
    def _soap_request(self, input_value):
        SOAP = self.service.version
        method = self.service.get_method('echoOperation')

        headers = SOAP.build_http_request_headers(method.soapAction)
        request_headers = self.as_django_client_headers(headers)
        tagname = method.input
        EchoType = self.service.schema.get_element_by_name('echoRequest')._type
        echo = EchoType.create(input_value)
        request_body = SOAP.Envelope.response(tagname, echo)
        return request_headers, request_body

    def _parse_soap_response(self, response_body):
        SOAP = self.service.version
        method = self.service.get_method('echoOperation')

        envelope = SOAP.Envelope.parsexml(response_body)
        assert_none(envelope.Body.Fault)
        output_element = self.service.schema.get_element_by_name(method.output)
        output_ = output_element._type.__class__
        return envelope.Body.parse_as(output_)

    def as_django_client_headers(self, headers):
        request_headers = {}
        for header_name, value in headers.items():
            key = 'HTTP_'+header_name.upper() if (header_name != 'content-type') else 'content_type'
            request_headers[key] = value
        return request_headers

    def django_settings(self):
        return AttrDict(
            DEFAULT_CHARSET='utf8',
            DEBUG=False,
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
            ],
            MIDDLEWARE_CLASSES = (
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware',
            ),
            CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}},
            SESSION_ENGINE='django.contrib.sessions.backends.cache',
            DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
            DEFAULT_TABLESPACE='',
            DEFAULT_INDEX_TABLESPACE='',
            ABSOLUTE_URL_OVERRIDES={},
            TRANSACTIONS_MANAGED=False,
            USE_TZ=True,
            FORCE_SCRIPT_NAME=None,
            DEBUG_PROPAGATE_EXCEPTIONS=True,
            SESSION_COOKIE_NAME='soapfish',
            SESSION_CACHE_ALIAS='default',
            SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer',
            USE_X_FORWARDED_HOST=False,
            USE_X_FORWARDED_PORT=False,
            SECURE_PROXY_SSL_HEADER=None,
            ALLOWED_HOSTS=['testserver'],
            CSRF_COOKIE_NAME='csrftoken',
            PREPEND_WWW=False,
            APPEND_SLASH=False,
            MESSAGE_STORAGE='django.contrib.messages.storage.fallback.FallbackStorage',
            USE_I18N=False,
            LANGUAGE_CODE='en',
            ROOT_URLCONF=None,
            DEFAULT_CONTENT_TYPE='text/html',
            SEND_BROKEN_LINK_EMAILS=False,
            USE_ETAGS=False,
            SESSION_SAVE_EVERY_REQUEST=False,
            LOGGING_CONFIG=None,
            LOGGING=None,
        )

