#coding=utf-8

from bs4 import BeautifulSoup
import requests, re, os
from urllib.parse import quote

def StreamUpdate(key, page = 1):
    print(key)
    URLs = "".join(['https://www.pixiv.net/search.php?word=', key, '&p=', str(page)])
    r = requests.Session()
    
    soup = BeautifulSoup(r.get(URLs).content, "lxml")
    body = soup.find('ul', '_image-items autopagerize_page_element')

    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
               'Referer' : 'https://www.pixiv.net/search.php?word=' + quote(key)}

    image_info = body.find_all('li', 'image-item')
    page_num = len(soup.find('div', 'pager-container').ul.find_all('li'))
    href= []; raw_img = []; title = []; auth = [];

    os.chdir(os.path.abspath('/PixivApp/static/cache'))
    
    for i in image_info[0:5]:
        title.append(i.find('h1', 'title').string)
        auth.append(i.find('a', 'user ui-profile-popup').string)
        href.append(i.a['href'])
        img_rp = r.get("".join(['https://www.pixiv.net/', i.a['href']]), headers = headers)
        src = BeautifulSoup(img_rp.content, "lxml").find('div','img-container').img['src']
        save_src = src.split('/img/')[1].replace('/', '-').strip()
        
        if not os.path.exists(save_src):
            with open(save_src, 'wb') as f:
                f.write(r.get(src, headers = headers).content)
            f.close()
        
        raw_img.append(save_src)
        
    return {'src' : raw_img, 'href' : href, 'auth' : auth, 'title' : title,
            'page_list' : [i for i in range(page, page_num + page)], 'current_page' : page}

     
