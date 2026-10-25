import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
import hiw  # noqa: E402


@pytest.fixture
def site(tmp_path, monkeypatch):
    """A small throwaway wiki; config points at it so the real Pages/ is never touched."""
    pages = tmp_path / "Pages"
    (pages / "ns" / "_assets").mkdir(parents=True)
    (pages / "_assets").mkdir()
    (pages / "wiki").mkdir()
    (pages / "start.md").write_text("# Start\n\nHello world\n\n## Section\n\n### Deep\n", encoding="utf-8")
    (pages / "ns" / "page.md").write_text("# Namespaced\n", encoding="utf-8")
    (pages / "wiki" / "sidebar.md").write_text("[[start|Home]]\n[[ns:page|NS]]\n", encoding="utf-8")
    (pages / "_assets" / "a.txt").write_text("root asset", encoding="utf-8")
    (pages / "ns" / "_assets" / "b.txt").write_text("ns asset", encoding="utf-8")
    monkeypatch.setattr(config, "siteBase", str(tmp_path))
    return tmp_path


@pytest.fixture
def client(site):
    hiw.app.config["TESTING"] = True
    return hiw.app.test_client()


def base_of(response):
    """The page fingerprint carried by the edit form."""
    return re.search(rb'name="base" value="([^"]*)"', response.data).group(1).decode()


def save(client, path, content, name="Ann", base=None):
    """Open the editor on a page and save content, like a browser would."""
    if base is None:
        base = base_of(client.get("/_edit/" + path + "/"))
    return client.post("/_edit/" + path + "/", data={"content": content, "name": name, "base": base})
