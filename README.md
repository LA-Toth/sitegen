sitegen
=======

It creates a static web site which can contain blog entries, and pages. The pages can be written as HTML code
(only the _content_ part of the page) or as Markdown.

Directory layout
================

As of now this directory structure is planned, some parts work already.

Source documents, templates, etc.
---------------------------------

* `pages` or `sources` (or both) contain the pages, either HTML or Markdown
* `posts` contains blog posts
* `_config.yml` contains site configuration
* `_layouts` contains page templates
* Makefile: controls sitegen
* any other directory without leading '_' or '.' characters are copied as is into its final place

As of now it's a bit different:
* `templates/current` contains the theme
   * `assets` subdirectory contains theme files needs to be copied into `_install/theme`
   * `default.tpl` is used to generate HTML files in `_install`
* `source` contains the `.md` files to be processed


During site generation
----------------------

* `_site` will be the location of the generated content
* `_build` is the directory used for temporary files

As of now the generated pages are in `_install` instead of `_site`.


Usage
=====

To initialize: `sitegen.py init -d my-site; cd my-site`

After initialization there will be a `Makefile`, which controls sitegen. As of now the dependency handling
is in that `Makefile`.

To generate files simply call `make` in the `my-site` directory.


