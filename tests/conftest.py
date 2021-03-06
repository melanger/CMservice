import os

import pytest
from OpenSSL import crypto

from cmservice.consent_request import ConsentRequest


@pytest.fixture(scope='session')
def cert_and_key(tmpdir_factory):
    tmpdir = str(tmpdir_factory.getbasetemp())
    cert_path = os.path.join(tmpdir, 'cert.pem')
    key_path = os.path.join(tmpdir, 'key.pem')
    create_self_signed_cert(cert_path, key_path)
    return cert_path, key_path


def create_self_signed_cert(cert_path, key_path):
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = 'US'
    cert.get_subject().ST = 'A'
    cert.get_subject().L = 'B'
    cert.get_subject().O = 'C'
    cert.get_subject().OU = 'ACME Inc.'
    cert.get_subject().CN = 'D'
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    with open(cert_path, 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(key_path, 'wb') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))


@pytest.fixture
def app_config(cert_and_key):
    config = dict(
        TESTING=True,
        DEBUG=True,
        TRUSTED_KEYS=[cert_and_key[0]],
        SECRET_KEY='fdgfds%€#&436gfjhköltfsdjglök34j5oö43ijtglkfdjgasdftglok432jtgerfd',
        TICKET_TTL=600,
        AUTO_SELECT_ATTRIBUTES=True,
        MAX_CONSENT_EXPIRATION_MONTH=12,
        USER_CONSENT_EXPIRATION_MONTH=[3, 6],
        CONSENT_SALT='VFT0yZ2dXzAHRlGb0cAhsac2ipKueybl8ZfuPzsHUrTZ8o7Vs6HnAlMhwbob',
    )
    return config


@pytest.fixture
def consent_request():
    consent_req_args = {
        'id': 'test_id',
        'redirect_endpoint': 'https://client.example.com/redirect',
        'attr': ['foo', 'bar']
    }
    return ConsentRequest(consent_req_args)
