import markdown
import pytest

import hiw


def render(text):
    return markdown.markdown(text, extensions=hiw.MD_EXTENSIONS)


def test_raw_html_is_escaped():
    out = render("<script>alert(1)</script>\n\nhi <b>x</b> <img src=x onerror=alert(1)>")
    assert "<script>" not in out and "<b>" not in out and "<img src" not in out
    assert "&lt;script&gt;" in out


@pytest.mark.parametrize("text", [
    "[x](javascript:alert(1))",
    "[x](JaVa\tScRiPt:alert(1))",
    "[x](  javascript:alert(1))",
    "[x](vbscript:x)",
    "![x](data:text/html;base64,AA)",
])
def test_unsafe_url_schemes_are_neutralised(text):
    out = render(text)
    assert "javascript" not in out.lower() and "data:" not in out and "vbscript" not in out
    assert '="#"' in out


def test_autolink_with_script_scheme_is_not_a_link():
    assert "<a" not in render("<javascript:alert(1)>")


@pytest.mark.parametrize("url", ["https://a.com/x", "http://a.com", "mailto:a@b.c", "/start/", "page", "#anchor", "?q=1"])
def test_safe_urls_are_kept(url):
    assert 'href="%s"' % url in render("[x](%s)" % url)


@pytest.mark.parametrize("url,expected", [
    ("javascript:x", "#"), ("  JAVASCRIPT:x", "#"), ("java\nscript:x", "#"),
    ("https://a.com", "https://a.com"), ("/rel", "/rel"), ("", ""),
])
def test_safeurl(url, expected):
    assert hiw.safeurl(url) == expected


def test_wikilinks():
    out = render("[[ns:page]] [[ns:page|Title]] [[page|Root title]]")
    assert '<a class="wikilink" href="/ns/page">ns:page</a>' in out
    assert '<a class="wikilink" href="/ns/page">Title</a>' in out
    assert 'href="/page">Root title</a>' in out


def test_image_embeds_with_sizes():
    assert '<img alt="a.png" src="/a.png" />' in render("![[a.png]]")
    assert 'width="300"' in render("![[a.png|300]]") and "height" not in render("![[a.png|300]]")
    out = render("![[a.png|300x200]]")
    assert 'width="300"' in out and 'height="200"' in out


@pytest.mark.parametrize("text", ["==hi there==", "???hi there???", "___hi there___"])
def test_highlighting(text):
    assert "<mark>hi there</mark>" in render(text)


def test_highlight_markers_are_literal_in_code_and_with_spaces():
    assert "<mark>" not in render("`==code==`")
    assert "<mark>" not in render("a == b == c")


def test_admonition_and_fenced_code():
    assert 'class="admonition note"' in render('!!! note "T"\n    body')
    assert "<pre><code>" in render("```\nx\n\ny\n```")
