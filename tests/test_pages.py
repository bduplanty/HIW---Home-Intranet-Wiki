import pytest

import config


def test_root_redirects_to_home_page(client, monkeypatch):
    assert client.get("/").headers["Location"].endswith("/start/")
    monkeypatch.setattr(config, "siteHome", "other")
    assert client.get("/").headers["Location"].endswith("/other/")


def test_pages_render(client):
    r = client.get("/start/")
    assert r.status_code == 200 and b"Hello world" in r.data
    r = client.get("/ns/page/")
    assert r.status_code == 200 and b"Namespaced" in r.data


@pytest.mark.parametrize("url", ["/nope/", "/ns/nope/", "/nope/page/", "/a/b/c/"])
def test_missing_pages_are_404(client, url):
    assert client.get(url).status_code == 404


@pytest.mark.parametrize("url", [
    "/..%2f..%2fetc/", "/%2e%2e/start/", "/ns/..%2fstart/", "/.history/start/",
    "/_edit/..%2fx/", "/_edit/%2e%2e/start/", "/_edit/a/b/c/",
    "/_history/%2e%2e/start/", "/_history/start/?v=../../x",
    "/%2e%2e/_assets/a.txt", "/_assets/..%2fstart.md",
])
def test_unsafe_paths_are_404(client, url):
    assert client.get(url).status_code == 404


def test_assets_are_served(client):
    assert client.get("/_assets/a.txt").data == b"root asset"
    assert client.get("/ns/_assets/b.txt").data == b"ns asset"
    assert client.get("/_assets/missing.txt").status_code == 404


def test_asset_prefix_follows_config():
    # the route is built from siteAssets when hiw is imported
    import hiw
    rules = {r.rule for r in hiw.app.url_map.iter_rules()}
    assert "/" + config.siteAssets + "/<filename>" in rules
    assert "/<namespace>/" + config.siteAssets + "/<filename>" in rules


def test_sidebar_comes_from_config(client, site, monkeypatch):
    assert b"Home" in client.get("/start/").data
    (site / "Pages" / "other.md").write_text("[[start|Elsewhere]]", encoding="utf-8")
    monkeypatch.setattr(config, "siteSidebar", "other")
    assert b"Elsewhere" in client.get("/start/").data


def test_missing_or_invalid_sidebar_does_not_break_pages(client, monkeypatch):
    monkeypatch.setattr(config, "siteSidebar", "nope/nope")
    assert client.get("/start/").status_code == 200
    monkeypatch.setattr(config, "siteSidebar", "../../etc/passwd")
    assert client.get("/start/").status_code == 200


def test_sidebar_style_option(client, monkeypatch):
    assert b'class="navpills"' in client.get("/start/").data
    monkeypatch.setattr(config, "siteSidebarPills", False)
    assert b"navpills" not in client.get("/start/").data


def test_logo_and_favicon_follow_config(client, monkeypatch):
    r = client.get("/favicon.ico")
    assert r.status_code == 200 and r.mimetype == "image/png"
    assert b'href="/static/logo.png"' in client.get("/start/").data
    monkeypatch.setattr(config, "siteLogo", "easymde/fontawesome-webfont.woff2")
    assert b"fontawesome-webfont.woff2" in client.get("/start/").data


def test_site_name_in_top_bar(client, monkeypatch):
    monkeypatch.setattr(config, "siteName", "My Wiki")
    assert b'<span class="sitename">My Wiki</span>' in client.get("/start/").data


def test_sitemap_lists_pages_and_skips_assets(client):
    html = client.get("/_sitemap/").data.decode()
    assert 'href="/start/"' in html and 'href="/ns/page/"' in html and 'href="/wiki/sidebar/"' in html
    assert "_assets" not in html and ".history" not in html
    assert b"Site Map" in client.get("/start/").data


def test_contents_panel_lists_h1_and_h2_only(client):
    html = client.get("/start/").data.decode()
    assert 'class="toc1"' in html and 'href="#start"' in html
    assert 'class="toc2"' in html and 'href="#section"' in html
    assert "Deep" not in html.split('id="toc"')[1].split("</details>")[0]


def test_no_contents_panel_without_headings(client, site):
    (site / "Pages" / "plain.md").write_text("just text", encoding="utf-8")
    assert b'id="toc"' not in client.get("/plain/").data
    assert b'id="toc"' not in client.get("/_edit/start/").data
