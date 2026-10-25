# Editing pages

## Starting an edit

Every page has a blue **Edit** pill in the top-right of the header. Click it to open the page in the editor (EasyMDE, a Markdown editor with a toolbar and preview). The address is `/_edit/<page>/` or `/_edit/<namespace>/<page>/`.

To **create a page**, edit an address that does not exist yet, for example `/_edit/ideas/`. The page is created when you save. Namespaces (folders) are created the same way: `/_edit/projects/plan/`.

Page and namespace names may use letters, numbers, spaces, `-` and `_` only.

## Your name

The first time you edit you are asked for your name. It is stored in a cookie (`hiw_editor`) for 30 days (`siteEditorCookie` and `siteEditorCookieDays` in `config.py`) and is renewed every time you save, so you are only asked again after a month without editing.

The editor shows *Editing as Name*. If that is not you (a shared computer, for example), click **not you?** and type a different name. The name is self-reported; there are no passwords.

Names are trimmed to 40 characters and anything other than letters, numbers, spaces, `-` and `_` is removed.

## Saving

Click **Save**. You are returned to the page, and the footer shows *Last edited by Name on 2026-10-24 14:44*. **Cancel** goes back without saving.

Saves are written to a temporary file and then swapped in, so a crash mid-save cannot leave a half-written page.

## Two people editing at once

When you open the editor, the form remembers a fingerprint (a SHA-1 hash) of the page as you saw it. On Save the server compares it with the page as it is now, inside a lock so only one save is checked at a time.

 - **Unchanged:** your save goes through.
 - **Changed by someone else since you opened it:** nothing is written. The editor reopens with your text intact and the message *This page was changed by Name at HH:MM since you opened it*. Open the current page in another tab, copy over what you need, then press **Save** again. That second save overwrites their version on purpose, and their version is still in the [[docs:history|history]].
 - **Two people creating the same new page:** the second one gets the same warning.

The lock covers one running server process, which is how HIW normally runs. If you run several worker processes, saves from different workers are only protected by the fingerprint check, which leaves a tiny window of milliseconds.
