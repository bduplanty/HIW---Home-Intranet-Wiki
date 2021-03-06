# Home Intranet Wiki (HIW)

[TOC]

This is my home wiki

## Set-up and information
- Use plaintext markdown files
  - defualt location is the Pages subdirectory
  - _asset subfolder used for organization
  - ``default.css`` can be overwritten or defined in the config

### Config.py
  - to have ``![[]]`` not default to ``_assets``, change siteAssets setting.  ``""`` will stay in current directory
  - ``siteCSS = "default.css"`` - the css file or when there is no override
  - ``siteCSSOverride = True`` - if a css file is in the pages folder or sub folder - TO BE IMPLEMENTED

------

## Syntax Reference
For markdown and markdown extra, see [[markdown-cheat-sheet]].
  
### Links
Also, regular linked markdown works:

  - ``[[markdown-cheat-sheet]]`` - intrawiki links (**same folder/namespace**) - [[markdown-cheat-sheet]]
  - ``[[markdown-cheat-sheet|Markdown Reference]]`` - interwiki link with title - [[markdown-cheat-sheet|Markdown Reference]]
  - ``[alt text](url) `` for links -- [Github](https://github.com/)
  - ``<http://azcastle.com>`` results in <http://azcastle.com> 

### Name Spaces
- folders inside the Pages directory
- ``[[:start]]`` - Root level link to page start - [[:start]]
- ``[[:start|Home]]`` - Root level link with title - [[:start|Home]]
- ``[[anamespace:nsstart]]`` - [[anamespace:nsstart]]
- ``[[anamespace:nsstart|NS1 Home]]`` - namespace page call with title - [[anamespace:nsstart|NS1 Home]]
- ``[anamespace:nsstart](/anamespace/nsstart)`` - [anamespace:nsstart](/anamespace/nsstart)

### Embeds

  - ``![image alt text](_assets/file)`` to embed an image
  
![An Image](/_assets/logo.png)

- ``![[_assets/logo.png]]``

![[_assets/logo.png]]

- ``![[_assets/logo.png|150]]`` to embed an image or file - set width
  
![[_assets/logo.png|150]]

- ``![[_assets/logo.png|50x150]]`` to embed an image or file - set size in #W#x#H# pattern
  
![[_assets/logo.png|50x150]]

### Admonitions

``!!! Note "This is an admonition - Note"``

!!! Note "This is an admonition - Note"

``!!! Tip "This is tip"``

!!! Tip "This is tip"

``!!! important "This is important"``

!!! important "This is important"

``!!! Warning "This is warning"``

!!! Warning "This is warning"

### Quotes
```
> This is an important quote - 1st line.
> Another line.
```

> This is an important quote - 1st line.
> Another line.

### Highlighting

``==This is highlighted.==``

==This is highlighted.==

This is not.

``???But this is!???``

???But this is!???


## Testing

>Lorem ipsum dolor sit amet, consectetur adipiscing elit. In lorem arcu, ultricies vitae nisi id, suscipit pulvinar turpis. Donec mattis euismod turpis, quis pulvinar ante sollicitudin vel. Aliquam ut leo lacus. Integer vitae ultricies dui, eget ornare metus. Mauris non lacus turpis. Donec commodo euismod magna vitae dictum. Etiam mattis aliquam egestas. Morbi nec leo nisl. Donec nulla mi, consequat quis interdum at, malesuada vel nunc.

!!! Tip "Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Phasellus at erat eget purus dictum lacinia vitae nec ex. Integer sit amet suscipit eros, non egestas ante. Morbi quis ligula ornare, tempus quam a, interdum magna. Suspendisse mauris mi, eleifend vitae est a, blandit venenatis urna. Sed commodo leo in tempus imperdiet. Maecenas purus sapien, scelerisque eget pulvinar sed, mollis ac purus. Nam ullamcorper accumsan gravida. Etiam sit amet semper nibh. Cras mattis tellus ut lobortis vehicula. Vivamus sit amet mauris nec enim aliquam dignissim vitae at mi. Integer auctor odio lorem, sed bibendum dui placerat a. Maecenas quam nunc, sagittis vel massa ut, viverra mattis dui. Nulla consectetur interdum dignissim. Curabitur at arcu dapibus, congue diam vitae, consequat nisl."

!!! Important "Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nunc est nibh, semper porta elit mattis, ullamcorper volutpat tortor. In hac habitasse platea dictumst. Aliquam mollis tristique augue eget rhoncus. Integer vel tortor facilisis, aliquet odio sit amet, convallis augue. Morbi tempor magna ut diam euismod, nec tempor nisl ornare. Pellentesque sapien felis, iaculis a cursus."

[Markdown Cheatsheet PDF](/_assets/markdown-cheat-sheet.pdf)