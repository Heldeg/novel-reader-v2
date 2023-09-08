from ebooklib import epub
import os
style = """

@namespace epub "http://www.idpf.org/2007/ops";

body {
    font-family: Bookerly, sans-serif, serif;
}
h1 {
    text-indent: 0;
    text-align: center;
    margin: 100px 0 0 0;
    font-size: 2.0em;
    font-weight: bold;
    page-break-before: always;
}
h2 {
    text-indent: 0;
    text-align: center;
    margin: 50px 0 0 0;
    font-size: 1.5em;
    font-weight: bold;
    page-break-before: always;
}

ol {
    list-style-type: none;
}
ol > li:first-child {
        margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}

p {
    text-indent: 1.25em;
    margin: 0;
}
img{
  display:block;
  width:100%; 
  height:100%;
  object-fit: cover;
}
"""
nav_css = epub.EpubItem(uid='style_nav', file_name="style/nav.css", media_type="text/css", content=style)


def setup_book(title, author, chapter_range: tuple, cover_url):
    book = epub.EpubBook()
    book.set_title(f"{title} {chapter_range[0]} - {chapter_range[1]}")
    book.set_language("es")
    book.add_author(author)
    img = open(cover_url, 'rb')
    book.set_cover("image.jpg", img.read())
    img.close()
    book.add_item(nav_css)
    return book


def prepare_content(title, raw_paragraphs):
    content = f"<h1>{title}</h1>"
    content += clean_text(raw_paragraphs)
    return content


def clean_text(raw_text):
    text_list = []
    text = ""
    for rt in raw_text:
        paragraph = rt.get_text()
        if paragraph not in text_list:
            text_list.append(paragraph)
            text += str(rt)
    return text


def create_new_chapter(chapter_title, raw_content, cap_num):
    new_chapter = epub.EpubHtml(title=chapter_title, file_name=f"chapter{cap_num}.xhtml")
    new_chapter.content = prepare_content(chapter_title, raw_content)
    new_chapter.add_item(nav_css)
    return new_chapter


def complete_book(chapter_list, directory, book_name, book):
    book.toc = chapter_list
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    index = book.get_item_with_href('nav.xhtml')
    index.add_item(nav_css)

    cover = book.get_item_with_href('cover.xhtml')
    cover.add_item(nav_css)
    my_spine = ['nav'] + chapter_list
    book.spine = my_spine
    if not os.path.exists(directory+'/caps'):
        os.makedirs(directory+'/caps')
    epub.write_epub(f'{directory}/caps/{book_name}', book, {})
