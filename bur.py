# coding:utf8
import requests
from bs4 import BeautifulSoup
import re
import xlwt
import os
from datetime import datetime
class News:
    def __init__(self,searchArea='news'):
        self.head = {
            'User-Agent' :"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/83.0.4103.106 Safari/537.36",
            'Cookie' : "_gid=GA1.2.1475031807.1592680742; ftn_cookie_id=1592680739.40596358; FTSTAT_ok_times=3; uniqueVisitorId=0df6b09c-deca-531f-2f0a-5db65d5fe2b8; FTSTAT_ok_pages=6; _gat_gtag_UA_1608715_1=1; _ga=GA1.1.884150484.1592680742; _ga_PDY0XG13PH=GS1.1.1592711759.3.1.1592712812.0; _ga_PT4E4NGVJV=GS1.1.1592711759.3.1.1592712812.0"
        }
        self.searchName = input('请输入要搜索的关键字：')
        self.searchArea = searchArea
        self.UrlData = []    #爬取新闻url的存储
        self.TitleData = []  #爬取新闻标题的存储
        self.NewsData = []  # 爬取新闻数据的存储
        self.pageCount = 0
        self.url ='http://m.ftchinese.com/search/?keys='+self.searchName + '&ftsearchType=' + self.searchArea + '&ie=utf-8'  #查找的关键字url
        print(self.url)
        self.dt=datetime.now()
 
    def get_page_count(self):

        #response = requests.get(url.format(self.searchName,self.searchArea))
        response = requests.get(url = self.url)
        print(response.text)
        # response.encoding = 'utf-8'
        html =response.text
        #得到的网页，判断是否有找到news
        soup =BeautifulSoup(html,'lxml')
        #print(soup)
        #爬取是否有l_v2这个class，如果有代表有数据，否则无
        try:
            page = soup.select('.l_v2')[0].text
        except Exception as e:
            page = ''
            print(e)
        if page !='' :
            purl = ''
            pageCount = re.findall(r'[0-9]\d*',page)
            for x in pageCount:
                purl = purl+x
            print(purl)
            self.pageCount = int(purl)//20 +1  #总的页数
        else:
            self.pageCount = 0
        return self.pageCount
 
    #get 整页的news
    def get_news_data(self):
        unaligned_flag = 0
        numb = 0
        url = 'http://m.ftchinese.com/search/?keys={}&ftsearchType={}&ie=utf-8&sort=time&page={}'
        count =input('共找到{}页信息，请输入需要爬取的页数，不输入按q继续【爬取全部】：'.format(self.pageCount))
        if count=='q':count = self.pageCount
        print('开始爬取......')
        for x in range(1,int(count)+1):
            responses = requests.get(url.format(self.searchName,self.searchArea,x),headers=self.head)
            html = responses.text
            soup = BeautifulSoup(html,'lxml')
            reg = soup.select('h2 a')
            # print(reg)
            newsUrl = re.findall('<a href="(.*?)" target="_blank">.*?</a>', str(reg),re.S)  # 新闻url
            print(newsUrl)
            newsUrl = list('http://m.ftchinese.com'+i for i in newsUrl)
            print(newsUrl)
            newsTitle = re.findall('<a href=".*?" target="_blank">(.*?)</a>', str(reg), re.S)   #新闻标题
            newsTitle =re.sub('<.*?>','',str(newsTitle))
            newsTitle = newsTitle[1:len(newsTitle)-1].replace("'",'')
            titleData = newsTitle.split(',') #新闻标题
            if (len(titleData) > len(newsUrl)):
                data_len = len(newsUrl)
                unaligned_flag = -1
            elif (len(titleData) < len(newsUrl)):
                data_len = len(titleData)
                unaligned_flag = 1
            else :
                data_len = len(titleData)
                unaligned_flag = 0
            for i in range(data_len):
                self.TitleData.append(titleData[i])
                self.UrlData.append(newsUrl[i])
                numb = numb + 1
                print(numb, newsUrl[i],i)
            i = 0
            # for i in range(len(titleData)):
            #     for j in range(len(titleData[i])):
            #             self.TitleData.append(titleData[i][j])
           
    
    def get_news_content(self,url):
        #根据得到的url，获取二级新闻页面的内容
        responses = requests.get(url,headers=self.head)
        responses.encoding = 'utf-8'
        html = responses.text
        soup = BeautifulSoup(html,'lxml')
        reg =soup.select('p')
        # regTitle = soup.select(('h1'))  # 获取页面标题  <h1 class="main-title">杨鸣：打3X3选郭少大韩做队友 颜值靠才华支撑</h1>
        # title = re.findall(r'.*?>(.*?)<.*?', str(regTitle[0]), re.S)
        # if len(title)>1:
        #     for i in range(len(title)-1):
        #         if title[i]!='':
        #             self.TitleData.append(title[i])
        #             break
        # else:
        #     self.TitleData.append(title[0])
        newsData = []  #用来装一条newscontent,二维
        newsData1 = []  # 用来装一条newscontent,1维
        #对<p><font> 这种格式做特殊处理
        if '<p><font>' in str(reg):
            reg = soup.select('p font')
            # print(reg)
            for x in reg:
                if len(x) > 0 and (self.searchName in str(x)):
                    data = re.findall('<font>(.*?)</font>', str(x),re.S)
                    newsData.append(data)
        else:
            #<p>这种格式默认处理
            for x in reg:
                if len(x) > 0 and (self.searchName in str(x)):
                    data = re.findall(r'<p(.*?)</p>', str(x),re.S)
                    newsData.append(data)
 
        #将二维数组转成一维存储入NewsData(新闻content)
        if len(newsData)==0 :
            newsData1 = []
        else :
            # print('newsData1 = {}'.format(newsData) )
            for i in range(len(newsData)-1):
                if newsData[i][0] != '':
                    newsData1.append(newsData[i][0])
                else:continue
        self.NewsData.append(newsData1)
 
 
     #封装后的入数据方法
    def final_func(self):
        self.save_data_excel()
 
 
    #将finalData存储到excel里面
    def save_data_excel(self):
        urldata = self.UrlData
        #newsdata = self.NewsData
        titledata = self.TitleData
        ExcelTitle = ['编号','新闻标题','URL']
        row = 0
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet('包含\"' +self.searchName +'\"的新闻',cell_overwrite_ok='True')
        #先写入第一行
        print('开始写入数据到excel....')
        for i in range(len(ExcelTitle)):
            sheet.write(row, i, ExcelTitle[i])
        print(len(titledata),len(self.TitleData))
        for j in range(len(titledata)):
            row += 1
            sheet.write(row, 0, row)
            sheet.write(row, 1, titledata[j])
            sheet.write(row, 2, urldata[j])
            print('%d ' %int(float( j ) /float(len(titledata)) * 100))
        book.save(self.dt.strftime( '%Y-%m-%d-%H-%M-%S' ) + '.csv')
        print('写入数据完毕！')
        print('../'+self.dt.strftime( '%Y-%m-%d-%H-%M-%S' ) + '.csv')
 
 
if __name__=='__main__':
    news = News('type_news')
    news.get_page_count()
    news.get_news_data()
    print('爬取完毕......')
    news.final_func()
    
 

