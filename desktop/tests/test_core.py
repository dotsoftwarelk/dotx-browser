import tempfile
import unittest
from pathlib import Path
from dotx.core import normalize_input, save_data, load_data

class CoreTests(unittest.TestCase):
    def test_search(self): self.assertEqual(normalize_input('hello world'), 'https://duckduckgo.com/?q=hello+world')
    def test_site(self): self.assertEqual(normalize_input('example.com/path'), 'https://example.com/path')
    def test_http(self): self.assertEqual(normalize_input('http://example.com'), 'http://example.com')
    def test_empty(self): self.assertEqual(normalize_input(' '), 'about:blank')
    def test_unsafe_scheme(self):
        for value in ['file:///etc/passwd', 'javascript://evil', 'https://u:p@example.com', 'https://example.com:xyz']:
            with self.subTest(value=value), self.assertRaises(ValueError): normalize_input(value)
    def test_save(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'nested' / 'state.json'
            save_data(path, {'bookmarks': ['hello']})
            self.assertEqual(load_data(path), {'bookmarks': ['hello']})
            path.write_text('invalid')
            self.assertEqual(load_data(path), {})
if __name__ == '__main__': unittest.main()
