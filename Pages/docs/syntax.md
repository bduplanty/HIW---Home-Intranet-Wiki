# Page syntax

Pages use [Markdown](https://daringfireball.net/projects/markdown/) with Python-Markdown's *extra* features (tables, footnotes, fenced code), a table of contents, and admonitions. See also [[markdown-cheat-sheet]].

## Links

    [[page]]                      link to a page in the root
    [[page|Title]]                the same, with your own link text
    [[namespace:page]]            link to a page inside a namespace
    [[namespace:page|Title]]      the same, with link text

## Images

Images live in an `_assets` folder: `Pages/_assets` for the root, `Pages/<namespace>/_assets` for a namespace.

    ![[logo.png]]                 image at natural size
    ![[logo.png|300]]             300 pixels wide
    ![[logo.png|300x200]]         300 wide, 200 high

## Highlighting

`==highlighted==`, `???highlighted???` and `___highlighted___` all produce highlighted text. Inside a code span or code block the markers are left alone.

## Admonitions

    !!! note "Title"
        Indented text of the note.

Types: `note`, `tip`, `warning`, `important`.

## Raw HTML is not allowed

HTML typed into a page is shown as text rather than run. This keeps one person's page from injecting scripts into everyone else's browser. Use Markdown for everything.

## Sidebar

The sidebar is the page `wiki/sidebar.md`. Edit it at `/_edit/wiki/sidebar/`.
