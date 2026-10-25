import os
import stat
import sys
import threading

import pytest

import config
import hiw
from conftest import base_of, save


def history(site, *names):
    folder = site / "Pages" / ".history" / "/".join(names[:-1]) / (names[-1] + ".md")
    return sorted(os.listdir(folder)) if folder.exists() else []


def test_first_edit_asks_for_a_name(client):
    r = client.get("/_edit/start/")
    assert r.status_code == 200
    assert b'name="name"' in r.data and b"easymde.min.js" in r.data
    assert b"Hello world" in r.data


def test_save_writes_page_snapshot_and_cookie(client, site):
    r = save(client, "start", "# New\r\n\r\nbody")
    assert r.status_code == 302 and r.headers["Location"].endswith("/start/")
    assert (site / "Pages" / "start.md").read_bytes() == b"# New\n\nbody"
    assert len(history(site, "start")) == 1 and history(site, "start")[0].endswith("__Ann.md")
    cookie = r.headers["Set-Cookie"]
    assert "hiw_editor=Ann" in cookie and "HttpOnly" in cookie and "Max-Age=2592000" in cookie and "SameSite=Lax" in cookie


def test_cookie_name_and_lifetime_follow_config(client, monkeypatch):
    monkeypatch.setattr(config, "siteEditorCookie", "other_cookie")
    monkeypatch.setattr(config, "siteEditorCookieDays", 7)
    cookie = save(client, "start", "x").headers["Set-Cookie"]
    assert "other_cookie=Ann" in cookie and "Max-Age=604800" in cookie
    assert b'name="name"' not in client.get("/_edit/start/").data
    monkeypatch.setattr(config, "siteEditorCookieDays", 0)
    assert "Max-Age" not in save(client, "start", "y").headers["Set-Cookie"]


def test_name_is_remembered_and_can_be_changed(client):
    save(client, "start", "one")
    page = client.get("/_edit/start/")
    assert b'name="name"' not in page.data and b"Editing as <strong>Ann</strong>" in page.data
    assert b'name="name"' in client.get("/_edit/start/?rename=1").data
    r = client.post("/_edit/start/", data={"content": "two", "name": "", "base": base_of(page)})
    assert r.status_code == 302                          # falls back to the cookie name


def test_missing_name_is_an_error_and_keeps_text_and_base(client, site):
    r = client.post("/_edit/start/", data={"content": "typed text", "name": "  ", "base": "opened-on"})
    assert r.status_code == 200 and b"Please enter your name" in r.data
    assert b">typed text</textarea>" in r.data and base_of(r) == "opened-on"
    assert history(site, "start") == []


def test_editor_name_is_sanitised(client, site):
    save(client, "start", "x", name="<b>Bob</b>/../x")
    assert history(site, "start")[0].endswith("__bBobbx.md")


def test_new_pages_and_namespaces_can_be_created(client, site):
    assert save(client, "fresh", "hello", base="").status_code == 302
    assert save(client, "newns/newpage", "hello", base="").status_code == 302
    assert (site / "Pages" / "fresh.md").exists() and (site / "Pages" / "newns" / "newpage.md").exists()
    assert b"hello" in client.get("/newns/newpage/").data


def test_footer_shows_editor_and_history_link(client):
    assert b"View Page History" in client.get("/start/").data
    assert b"Last edited on" in client.get("/start/").data          # file time only
    save(client, "start", "x")
    html = client.get("/start/").data
    assert b"Last edited by Ann on" in html and b'href="/_history/start/"' in html


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permissions")
def test_save_keeps_file_permissions(client, site):
    page = site / "Pages" / "start.md"
    os.chmod(page, 0o664)
    save(client, "start", "x")
    assert stat.S_IMODE(os.stat(page).st_mode) == 0o664
    save(client, "brandnew", "x", base="")
    assert stat.S_IMODE(os.stat(site / "Pages" / "brandnew.md").st_mode) == 0o644


def test_no_temp_files_left_behind(client, site):
    save(client, "start", "x")
    assert [f for f in os.listdir(site / "Pages") if f.endswith(".tmp")] == []


def test_stale_save_is_refused_and_text_kept(client, site):
    opened = base_of(client.get("/_edit/start/"))
    other = hiw.app.test_client()
    assert save(other, "start", "Bob's version", name="Bob").status_code == 302
    r = client.post("/_edit/start/", data={"content": "my version", "name": "Ann", "base": opened})
    assert r.status_code == 200 and b"changed by Bob" in r.data and b">my version</textarea>" in r.data
    assert (site / "Pages" / "start.md").read_text() == "Bob's version"
    # pressing Save again (the form now carries the new base) overwrites on purpose
    r = client.post("/_edit/start/", data={"content": "my version", "name": "Ann", "base": base_of(r)})
    assert r.status_code == 302
    assert (site / "Pages" / "start.md").read_text() == "my version"
    assert [h.split("__")[1] for h in history(site, "start")] == ["Bob.md", "Ann.md"]   # Bob's version stays in the history


def test_two_people_creating_the_same_page_conflict(client):
    other = hiw.app.test_client()
    assert save(client, "race", "A", base="").status_code == 302
    assert save(other, "race", "B", base="").status_code == 200


def test_simultaneous_saves_only_one_wins(client, site):
    clients = [hiw.app.test_client() for _ in range(8)]
    opened = base_of(client.get("/_edit/start/"))
    results = []

    def go(c, n):
        results.append(c.post("/_edit/start/", data={"content": "v%d" % n, "name": "P%d" % n, "base": opened}).status_code)

    threads = [threading.Thread(target=go, args=(c, n)) for n, c in enumerate(clients)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert sorted(results) == [200] * 7 + [302]
    assert len(history(site, "start")) == 1


def test_saves_in_the_same_second_get_separate_snapshots(client, site):
    for n in range(3):
        save(client, "start", "v%d" % n)
    assert len(set(history(site, "start"))) == 3


def test_latest_editor_is_the_last_saver_even_within_one_second(client, site):
    other = hiw.app.test_client()
    save(other, "start", "by Bob", name="Bob")
    save(client, "start", "by Ann", name="Ann", base=hiw.pageversion(("start",)))
    editor, _ = hiw.lastedit(("start",), str(site / "Pages" / "start.md"))
    assert editor == "Ann"


def test_attribution_ignores_stray_history_files(client, site):
    save(client, "start", "x")
    folder = site / "Pages" / ".history" / "start.md"
    (folder / "README.txt").write_text("stray")
    (folder / "zzz.md").write_text("stray")
    editor, when = hiw.lastedit(("start",), str(site / "Pages" / "start.md"))
    assert editor == "Ann" and when is not None


def test_lastedit_falls_back_to_file_time(site):
    editor, when = hiw.lastedit(("start",), str(site / "Pages" / "start.md"))
    assert editor is None and when is not None
    assert hiw.lastedit(("nope",), str(site / "Pages" / "nope.md")) == (None, None)
