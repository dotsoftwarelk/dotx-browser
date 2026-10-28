import unittest
from dotx.services.github_device import parse_challenge, parse_poll, validate_client_id, valid_login, DEVICE_VERIFY_URL

class DeviceFlowTests(unittest.TestCase):
    def challenge(self):
        return {'device_code':'abc123456789', 'user_code':'ABCD-1234', 'verification_uri':DEVICE_VERIFY_URL, 'expires_in':900, 'interval':5}
    def test_client_id(self):
        self.assertTrue(validate_client_id('Ov123456789abc'))
        for value in ('', 'short', 'bad space here', 'x'*101): self.assertFalse(validate_client_id(value))
    def test_challenge(self):
        c=parse_challenge(self.challenge()); self.assertEqual(c.interval,5);self.assertEqual(c.expires_in,900)
    def test_bad_uri_and_timing(self):
        for key,value in [('verification_uri','https://github.com.evil/login/device'),('interval',-1),('expires_in',0),('user_code','bad')]:
            doc=self.challenge();doc[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):parse_challenge(doc)
    def test_polling(self):
        self.assertEqual(parse_poll({'error':'authorization_pending'},5),('pending',5,None))
        self.assertEqual(parse_poll({'error':'slow_down','interval':12},5),('pending',12,None))
        self.assertEqual(parse_poll({'error':'slow_down'},5),('pending',10,None))
        self.assertEqual(parse_poll({'error':'access_denied'},5),('access_denied',5,None))
        self.assertEqual(parse_poll({'error':'expired_token'},5),('expired_token',5,None))
        self.assertEqual(parse_poll({'access_token':'sample-token','token_type':'bearer'},5),('authorized',5,'sample-token'))
        self.assertEqual(parse_poll({'error':'unknown'},5),('error',5,None))
        self.assertEqual(parse_poll({'access_token':'sample-token', 'token_type':None},5),('error',5,None))
    def test_identity_validation(self):
        self.assertEqual(valid_login({'login':'dotsoftwarelk'}),'dotsoftwarelk')
        self.assertIsNone(valid_login({'login':'evil<script>'}))
        self.assertIsNone(valid_login({'login':None}))
if __name__=='__main__':unittest.main()
