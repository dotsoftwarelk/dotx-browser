"""Optional Playwright browser QA against a running local site (default :8001)."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE = os.environ.get('DOTX_TEST_SITE', 'http://127.0.0.1:8001/')
run = {'id': 42, 'head_branch': 'main', 'conclusion': 'success', 'head_sha': 'a' * 40}
artifact = {'name': 'DOTX-Windows-development-unsigned', 'expired': False, 'expires_at': '2100-01-01T00:00:00Z'}
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width': 1440, 'height': 900}, color_scheme='dark')
    page = context.new_page(); errors=[]; page.on('pageerror',lambda e: errors.append(str(e)))
    def handle(route):
        body = {'artifacts': [artifact]} if route.request.url.endswith('/artifacts') else {'workflow_runs':[run]}
        route.fulfill(json=body)
    page.route('https://api.github.com/**',handle)
    page.goto(BASE,wait_until='networkidle')
    assert page.title() == 'Home | DOTX Browser'
    assert page.locator('.product-visual img').evaluate('(e) => e.complete && e.naturalWidth > 0')
    assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth')
    dark = page.locator('body').evaluate('(e) => getComputedStyle(e).backgroundColor')
    page.locator('#theme-picker').select_option('light')
    light = page.locator('body').evaluate('(e) => getComputedStyle(e).backgroundColor')
    assert dark != light
    page.reload(wait_until='networkidle'); assert page.locator('#theme-picker').input_value() == 'light'
    page.screenshot(path='/home/user/dotx-website-light-check.png',full_page=True)
    page.goto(BASE+'download.html',wait_until='networkidle')
    assert page.locator('#build-link').is_visible()
    assert page.locator('#build-link').get_attribute('href').endswith('/runs/42')
    assert 'source aaaaaaa' in page.locator('#build-status').inner_text()
    for path in ['features.html','integrations.html','docs.html','privacy.html','security.html','faq.html','about.html','changelog.html','404.html']:
        response=page.goto(BASE+path,wait_until='domcontentloaded')
        assert response.status == 200 and page.locator('h1').count()==1, path
    assert not errors, errors
    # Emulate GitHub Pages serving the custom 404 for a deep project URL.
    html = Path('site/404.html').read_text(encoding='utf-8').replace('<base href="/">', '<base href="/dotx-browser/">')
    def subpath(route):
        if route.request.url.endswith('/dotx-browser/missing/nested'):
            route.fulfill(status=404, content_type='text/html', body=html)
        else:
            target = route.request.url.replace('/dotx-browser/', '/', 1)
            route.fulfill(response=route.fetch(url=target))
    page.route('**/dotx-browser/**',subpath)
    assert page.goto(BASE+'dotx-browser/missing/nested').status == 404
    assert page.locator('.brand').first.evaluate('(e) => e.href').endswith('/dotx-browser/index.html')
    assert page.locator('link[rel="stylesheet"]').evaluate('(e) => !!e.sheet')
    context.close()
    mobile=browser.new_context(viewport={'width':375,'height':812},is_mobile=True,has_touch=True,color_scheme='light')
    page=mobile.new_page(); page.goto(BASE,wait_until='networkidle')
    assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth')
    page.locator('.mobile-nav summary').click()
    assert page.locator('.mobile-nav').evaluate('(e) => e.open')
    page.locator('.mobile-nav a[href="docs.html"]').click()
    assert page.url.endswith('/docs.html')
    page.screenshot(path='/home/user/dotx-website-mobile-check.png',full_page=True)
    mobile.close()
    nojs=browser.new_context(java_script_enabled=False, color_scheme='light')
    page=nojs.new_page();page.goto(BASE+'download.html',wait_until='domcontentloaded')
    assert page.locator('noscript').count()==1 and not page.locator('#build-link').is_visible()
    nojs.close();browser.close()
print('PASS: Chromium desktop/mobile, local assets, pages, theme persistence, mobile menu, mocked download metadata, project-subpath 404 and no-JS fallback')
