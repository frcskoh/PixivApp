from bs4 import BeautifulSoup
import requests, re, os
from urllib.parse import quote

def StreamUpdate(key, page = 1):
    work_path = os.getcwd()
    print(key)
    URLs = "".join(['https://www.pixiv.net/search.php?word=', key, '&p=', str(page)])
    headers = {'Referer' : 'https://www.pixiv.net/',
               'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
               }
    
    for i in range(10):
        print('retry : ' + str(i))
        soup = BeautifulSoup(requests.get(URLs, headers = headers).content, "lxml")
        if soup.find('ul', '_image-items autopagerize_page_element'): break
    print(soup.prettify())
    body = soup.find('ul', '_image-items autopagerize_page_element')

    info_headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
               'Referer' : 'https://www.pixiv.net/search.php?word=' + quote(key)}

    image_info = body.find_all('li', 'image-item')

    if soup.find('ul', 'page-list'):
        page_num = len(soup.find('ul', 'page-list').find_all('li')) - 2
    else:
        page_num = 1
    
    href= []; raw_img = []; title = []; auth = []; auth_href = []; ID = [];
    
    if not os.path.exists(os.path.join(os.getcwd(), 'static', 'cache')):
        os.mkdir(os.path.join(os.getcwd(), 'static', 'cache'))
    os.chdir(os.path.join(os.getcwd(), 'static', 'cache'))
    
    r = requests.Session()
    for i in image_info:
        title.append(i.find('h1', 'title').string)
        auth.append(i.find('a', 'user ui-profile-popup').string)
        auth_href.append("")
        ID.append(i.find('a', 'user ui-profile-popup')['href'].split('=')[-1])
        href.append(i.a['href'])
        img_rp = r.get("".join(['https://www.pixiv.net/', i.a['href']]), headers = info_headers)
        img_url = BeautifulSoup(img_rp.content, "lxml").find('div','img-container').img['src']
        print(img_url)
        
        save_src = img_url.split('/img/')[1].replace('/', '-').strip()

        if not os.path.exists(save_src):
            with open(save_src, 'wb') as f:
                f.write(r.get(img_url, headers = headers).content)
        
        raw_img.append(save_src)

    data = {
            'src' : raw_img, 'href' : href, 'auth' : auth, 'title' : title,
            'page_list' : [i for i in range(page, page_num + page)], 'current_page' : page,
            'length' : len(raw_img), 'auth_href' : auth_href, 'ID' : ID 
            }

    os.chdir(work_path)
    return data

def ImageBuilder(ID):
    print(ID)
    URL = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + ID 
    headers = {'Referer' : 'https://www.pixiv.net/',
               'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
               }
    soup = BeautifulSoup(requests.get(URL, headers = headers).content, "lxml")

    body = soup.find('div', 'cool-work-main')
    titlearea = body.find('div', 'titlearea')
    
    user = {
            'icon' : titlearea.find('div', 'usericon').img['src'],
            'href' : titlearea.find('div', 'usericon').a['href'],
            'auth' : titlearea.find('div', 'userdata').h2.a.string,
            'date' : titlearea.find('div', 'userdata').span.string
            }

    return user
