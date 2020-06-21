import requests
from bs4 import BeautifulSoup
from lxml import etree

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
url = 'http://newgame.17173.com/game-list-0-0-0-0-0-0-0-0-0-0-1-2.html'

r = requests.get(url)
soup = BeautifulSoup(r.text,'lxml')
info_list = soup.find_all(attrs = {'class':'pylist ptlist-pc'})
tit_list = info_list[0].find_all(attrs = {'class':'tit'})
for title in tit_list:
  print(title.text.replace('\n',''))