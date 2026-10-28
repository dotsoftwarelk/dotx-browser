import json
import unittest
from urllib.parse import parse_qs, urlsplit
from dotx.services.github import search_url, parse_results, error_message

class GitHubPublicSearchTests(unittest.TestCase):
    def test_query_encoded(self):
        url = urlsplit(search_url('qt browser & stars:>100'))
        self.assertEqual(url.hostname, 'api.github.com')
        self.assertEqual(parse_qs(url.query)['q'], ['qt browser & stars:>100'])
    def test_empty_and_oversize(self):
        for q in (' ', 'x'*201):
            with self.assertRaises(ValueError): search_url(q)
    def test_valid_and_untrusted_results(self):
        data={'items':[{'full_name':'a/b','html_url':'https://github.com/a/b','description':'ok','stargazers_count':7},
            {'full_name':'fake','html_url':'https://github.com.evil.invalid/a','description':'x'},
            {'full_name':'fake2','html_url':'https://u:p@github.com/a','description':'x'}, None]}
        result=parse_results(json.dumps(data).encode())
        self.assertEqual(len(result),1); self.assertEqual(result[0].stars,7)
    def test_bad_response(self):
        for raw in (b'broken',b'{}',b'x'*1_000_001):
            with self.assertRaises(ValueError): parse_results(raw)
    def test_rate_limit(self):
        self.assertIn('rate limit',error_message(403,True))
        self.assertIn('rate limit',error_message(429))
        self.assertIn('denied',error_message(403))
if __name__=='__main__': unittest.main()
