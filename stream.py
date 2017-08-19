from bs4 import BeautifulSoup
import requests, sys, re, os, json
from urllib.parse import quote
from multiprocessing import Pool, freeze_support, cpu_count
sys.setrecursionlimit(1000000)

def ImageBuilder(ID, headers, image_headers, cache_path):
    URL = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + ID
    r = requests.Session()
    soup = BeautifulSoup(r.get(URL, headers = headers).content, "lxml")
    body = soup.find('div', 'cool-work-main')
    if body:
        titlearea = body.find('div', 'titlearea')
        icon_url = titlearea.find('div', 'usericon').img['src'].replace('gif', 'png')
        save_src = icon_url.split('/img/')[-1].replace('/', '-').strip()
        
        write_path = os.path.join(cache_path, save_src)
        if not os.path.exists(write_path):
            with open(write_path, 'wb') as f:
                f.write(r.get(icon_url, headers = image_headers).content)
        
        user = {
                "ID" : ID, 
                "date" : titlearea.find('div', 'userdata').span.string, 
                "icon" : save_src, 
                "auth_href" : titlearea.find('div', 'usericon').a['href'],
                "caption" : soup.find('div', 'caption').string
                }
    else:
        user = None
    
    return user

def DataReceive(r, part, headers, image_headers, cache_path):
    #print(os.getpid())
    t_ID = part.find('a', 'user ui-profile-popup')['data-user_id']
    t_info = ImageBuilder(t_ID, headers, image_headers, cache_path)
    if t_info:
        t_title = part.find('h1', 'title').string
        t_auth = part.find('a', 'user ui-profile-popup').string
        t_href = "".join(['https://www.pixiv.net/', part.a['href']])
        for i in range(10):
            try:
                img_rp = None
                img_rp = r.get(t_href, headers = headers)
            except:
                pass
            else:
                break
        
        img_url = BeautifulSoup(img_rp.content, "lxml").find('div','img-container').img['src']
        #print(img_url)
        t_save_src = img_url.split('/img/')[-1].replace('/', '-').strip()

        write_path = os.path.join(cache_path, t_save_src)
        if not os.path.exists(write_path):
            with open(write_path, 'wb') as f:
                f.write(r.get(img_url, headers = image_headers).content)
        
        data = {
            "title" : t_title,
            "auth" : t_auth,
            "href" : t_href, 
            "save_src" : t_save_src, 
            "img_info" : t_info
            }
        return json.dumps(data)
    else:
        return None

def StreamUpdate(key, page = 1, headers = {'Referer' : 'https://www.pixiv.net/',
                                           'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
                                           }):
    image_headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Referer' : 'https://www.pixiv.net/search.php?word=' + quote(key)
        }
    
    work_path = os.getcwd()
    print(key)
    URLs = "".join(['https://www.pixiv.net/search.php?word=', key, '&p=', str(page)])
    
    for i in range(10):
        print('retry : ' + str(i))
        soup = BeautifulSoup(requests.get(URLs, headers = headers).content, "lxml")
        if soup.find('ul', '_image-items autopagerize_page_element'): break

    body = soup.find('ul', '_image-items autopagerize_page_element')
    image_info = body.find_all('li', 'image-item')

    
    page_num = len(soup.find('ul', 'page-list').find_all('li')) - 2 if soup.find('ul', 'page-list') else 1

    #switch the dicty
    cache_path = os.path.join(os.getcwd(), 'static', 'cache')
    if not os.path.exists(cache_path): os.mkdir(cache_path)
    
    r = requests.Session()
   
    freeze_support()
    pool = Pool(processes = cpu_count() << 2)
    pool_result = [pool.apply_async(DataReceive, args = (r, i, headers, image_headers, cache_path, )) for i in image_info]
    pool.close()
    pool.join()

    content = []
    for process in pool_result:
        if process.get():
            content.append(json.loads(process.get()))
    
    os.chdir(work_path)
    return {
        'content' : content, 
        'current_page' : page, 
        'page_list' : [i for i in range(page_num)],
        'length' : len(content)
        }
