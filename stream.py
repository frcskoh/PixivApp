from bs4 import BeautifulSoup
import requests, re, os
from urllib.parse import quote

def StreamUpdate(key, page = 1):
    print(key)
    URLs = "".join(['https://www.pixiv.net/search.php?word=', key, '&p=', str(page)])
    headers = {'Referer' : 'https://www.pixiv.net/',
               'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
               }
    r = requests.Session()
    
    soup = BeautifulSoup(r.get(URLs, headers = headers).content, "lxml")
    print(soup.prettify())
    body = soup.find('ul', '_image-items autopagerize_page_element')

    info_headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
               'Referer' : 'https://www.pixiv.net/search.php?word=' + quote(key)}

    image_info = body.find_all('li', 'image-item')
    page_num = len(soup.find('div', 'pager-container').ul.find_all('li')) - 2
    href= []; raw_img = []; title = []; auth = [];

    os.chdir(os.path.abspath('/PixivApp/static'))
    if not os.path.exists('cache'):
        os.mkdir('cache')
    os.chdir('cache')
    
    for i in image_info:
        title.append(i.find('h1', 'title').string)
        auth.append(i.find('a', 'user ui-profile-popup').string)
        href.append(i.a['href'])
        img_rp = r.get("".join(['https://www.pixiv.net/', i.a['href']]), headers = info_headers)
        src = BeautifulSoup(img_rp.content, "lxml").find('div','img-container').img['src']
        save_src = src.split('/img/')[1].replace('/', '-').strip()
        
        if not os.path.exists(save_src):
            with open(save_src, 'wb') as f:
                f.write(r.get(src, headers = headers).content)
        
        raw_img.append(save_src)

    data = {
            'src' : raw_img, 'href' : href, 'auth' : auth, 'title' : title,
            'page_list' : [i for i in range(page, page_num + page)], 'current_page' : page,
            'length' : len(raw_img)
            }
    return data

def ImageBuilder(ID):
    URL = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + ID
    r = requests.Session()
    headers = {'Referer' : 'https://www.pixiv.net/',
               'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
               }
    soup = BeautifulSoup(r.get(URL, headers = headers).content, "lxml")

    body = soup.find('div', 'cool-work-main')
    titlearea = body.find('div', 'titlearea')
    
    user = {
            'icon' : titlearea.find('div', 'usericon').img['src'],
            'href' : titlearea.find('div', 'usericon').a['href'],
            'name' : titlearea.find('div', 'userdata').h2.a.string,
            'date' : titlearea.find('div', 'userdata').span.string
            }

    return user

    


    
