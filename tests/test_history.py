import re

import pytest

from conftest import base_of, save


def test_empty_history(client):
    r = client.get("/_history/start/")
    assert r.status_code == 200 and b"No versions have been saved" in r.data


def test_history_lists_views_and_restores(client, site):
    save(client, "start", "first version")
    save(client, "start", "second version", name="Bob")
    html = client.get("/_history/start/").data.decode()
    versions = re.findall(r'\?v=(\d{8}T\d{6}__\w+)', html)
    assert len(versions) == 2 and "(latest)" in html
    assert versions[0].endswith("__Bob") or versions[0].endswith("__Ann")

    old = [v for v in versions if v.endswith("__Ann")][0]
    page = client.get("/_history/start/?v=" + old)
    assert page.status_code == 200 and b"first version" in page.data and b"Restore this version" in page.data

    editor = client.get("/_edit/start/?restore=" + old)
    assert b">first version</textarea>" in editor.data
    # restoring is just another save, so it creates a new version
    assert save(client, "start", "first version", base=base_of(editor)).status_code == 302
    assert len(re.findall(r"\?v=", client.get("/_history/start/").data.decode())) == 3
    assert (site / "Pages" / "start.md").read_text() == "first version"


def test_namespace_page_history(client):
    save(client, "ns/page", "changed")
    assert b"Ann" in client.get("/_history/ns/page/").data


@pytest.mark.parametrize("version", ["nope", "../../x", "20990101T000000__Ghost", "20260101T000000__a/b", ""])
def test_bad_versions_are_404(client, version):
    save(client, "start", "x")
    if version:
        assert client.get("/_history/start/?v=" + version).status_code == 404
    assert client.get("/_edit/start/?restore=" + (version or "zzz")).status_code == 404


def test_history_is_per_page(client):
    save(client, "start", "x")
    version = re.search(r"\?v=(\S+?)\"", client.get("/_history/start/").data.decode()).group(1)
    assert client.get("/_history/ns/page/?v=" + version).status_code == 404
