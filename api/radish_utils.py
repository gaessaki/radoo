# -*- coding: utf-8 -*-
import html2text


def radish_html2text(html):
    if not html:
        return html
    converter = html2text.HTML2Text()
    # You can see available options here:
    # https://github.com/Alir3z4/html2text/blob/master/docs/usage.md
    converter.ignore_links = True
    converter.images_to_alt = True
    converter.ignore_tables = True
    converter.ignore_emphasis = True
    converter.use_automatic_links = False
    converter.single_line_break = False
    converter.body_width = 0
    text = converter.handle(html)
    return text.strip("\n\r\t ")
