import json
import unittest
from urllib.parse import parse_qs, urlsplit
from dotx.services.github import search_url, search_issues_url, parse_results, parse_issues, error_message

class GitHubPublicSearchTests(unittest.TestCase):
    def test_query_encoded(self):
        url = urlsplit(search_url('qt browser & stars:>100'))
        self.assertEqual(url.hostname, 'api.github.com')
        self.assertEqual(parse_qs(url.query)['q'], ['qt browser & stars:>100'])
    def test_empty_and_oversize(self):
        for q in (' ', 'x'*201):
            with self.assertRaises(ValueError): search_url(q)
            with self.assertRaises(ValueError): search_issues_url(q)
    def test_valid_and_untrusted_results(self):
        data={'items':[{'full_name':'a/b','html_url':'https://github.com/a/b','description':'ok','stargazers_count':7},
            {'full_name':'fake','html_url':'https://github.com.evil.invalid/a','description':'x'},
            {'full_name':'fake2','html_url':'https://u:p@github.com/a','description':'x'},
            {'full_name':'a/b','html_url':'https://github.com/a/b/settings'},
            {'full_name':'a/b','html_url':'https://github.com/a/b?next=elsewhere'},
            {'full_name':'a/b','html_url':'https://github.com/x/y'},
            {'full_name':'../..','html_url':'https://github.com/../..'}, None]}
        result=parse_results(json.dumps(data).encode())
        self.assertEqual(len(result),1); self.assertEqual(result[0].stars,7)
    def test_bad_response(self):
        for raw in (b'broken',b'{}',b'x'*1_000_001):
            with self.assertRaises(ValueError): parse_results(raw)
            with self.assertRaises(ValueError): parse_issues(raw)
    def test_public_issue_search(self):
        query = parse_qs(urlsplit(search_issues_url('repo:python/cpython bug')).query)['q'][0]
        self.assertEqual(query, 'repo:python/cpython bug is:issue')
        data = {'items': [
            {'title': 'A bug', 'html_url': 'https://github.com/python/cpython/issues/12', 'number': 12, 'state': 'open'},
            {'title': 'pull', 'html_url': 'https://github.com/python/cpython/pull/13', 'number': 13, 'state': 'open', 'pull_request': {}},
            {'title': 'fake', 'html_url': 'https://github.com.evil/python/cpython/issues/14', 'number': 14, 'state': 'open'},
            {'title': 'dot segments', 'html_url': 'https://github.com/../cpython/issues/1', 'number': 1, 'state': 'open'},
            {'title': 'query', 'html_url': 'https://github.com/python/cpython/issues/15?x=1', 'number': 15, 'state': 'open'},
            {'title': 'wrong number', 'html_url': 'https://github.com/python/cpython/issues/15', 'number': 16, 'state': 'open'}]}
        result = parse_issues(json.dumps(data).encode())
        self.assertEqual(len(result), 1); self.assertEqual(result[0].repository, 'python/cpython')
        self.assertEqual(result[0].number, 12)
    def test_rate_limit(self):
        self.assertIn('rate limit',error_message(403,True))
        self.assertIn('rate limit',error_message(429))
        self.assertIn('denied',error_message(403))
if __name__=='__main__': unittest.main()
