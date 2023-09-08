import urllib.request, urllib.parse, urllib.error
import ssl
from bs4 import BeautifulSoup
import re

tags_to_search = ["p", "table"]

greek_num = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}

cap_num_error = -1
curren_chapter = 0

# https://untitled-translation.fukou-da.net/death-mage/the-death-mage-that-doesnt-want-a-fourth-time-267/
# https://tunovelaligera.com/super-gene/super-god-gene-capitulo-1-editado/
# https://readnovelfull.org/the-crazy-knights-age-of-the-universe/chapter-1-black-history-and-testament
# https://novelfull.com/global-reincarnation-becoming-a-god-with-my-unlimited-revive/chapter-411-elven-archer.html
# https://tunovelaligera.com/wmw-tnl/warlock-of-the-magus-world-capitulo-126-tnl/
# https://tunovelaligera.com/larga-vida-a-las-invocaciones/larga-vida-a-las-invocaciones-capitulo-630/
# https://tunovelaligera.com/diario-experimental-del-loco-lich/elcl-capitulo-1/

def create_page_ctx():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def get_page(url: str, context):
    try:     
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        return urllib.request.urlopen(req, context=context).read()
    except urllib.error.HTTPError as e:
        print("Error in chapter",curren_chapter+1, "Error:",e)
        url = input("New Url: ")
        return get_page(url, context)



def get_content(bs):
    re_h = re.compile("cap[i,í]tulo", flags=re.IGNORECASE)
    text = bs.find_all(tags_to_search, {"hidden": False, 'class': None})
    if len(text) < 5:
        text = bs.find_all(tags_to_search + ['div'], {"hidden": False, 'class': None})[:-9]
    titles_h1 = bs.find_all("h1", text=re_h)
    titles_h2 = bs.find_all("h2", text=re_h)
    titles_h3 = bs.find_all("h3", text=re_h)
    titles_p = list(filter(lambda x: re_h.search(x.get_text()), text[:5]))
    titles = titles_h1 + titles_h3 + titles_p + titles_h2
    return text, titles, bs.find_all("a")


def get_next_chapter_url(a_list):
    next_chapter_regx = re.compile(r"[a-z\s]*(siguiente|next)[a-z\s]*", flags=re.IGNORECASE)
    return list(filter(lambda x: next_chapter_regx.match(x.get_text()), a_list))


def get_title(h_list):
    global cap_num_error, curren_chapter
    # TODO: Greek numbers
    re_h = re.compile("(cap[i,í]tulo ([0-9IV]+)(.*))", flags=re.IGNORECASE)
    try:
        regx_text = re_h.search(h_list[0].get_text())
        title = regx_text.group(1)
        try:
            cap_num = int(regx_text.group(2))
        except ValueError:
            cap_num = greek_num[regx_text.group(2)]
        curren_chapter = cap_num
    except (IndexError, AttributeError):
        if cap_num_error == -1:
            curren_chapter = int(input("Enter chapter number: "))
        else:
            curren_chapter += 1
        cap_num_error += 1    
        cap_num = curren_chapter
        title = f"Capítulo {cap_num}"
        print("error with the title", curren_chapter)
    return title, cap_num


def get_chapter_href(next_chapter):
    try:
        return next_chapter[0].get("href", None)
    except IndexError:
        return False


def get_chapter(url):
    context = create_page_ctx()
    html_content = get_page(url, context)
    soup = BeautifulSoup(html_content, 'html.parser')
    content, headers, links = get_content(soup)
    next_chapter_link = get_next_chapter_url(links)
    return content, get_title(headers), get_chapter_href(next_chapter_link)
