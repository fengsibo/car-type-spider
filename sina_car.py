# encoding=utf-8
import requests
from urllib import request
import urllib.request
import socket, re, os, time
import urllib.error
from selenium import webdriver
from lxml import etree
import concurrent.futures


class spider():
    def __init__(self, main_page, save_path):
        self.main_page = main_page
        self.driver = webdriver.PhantomJS('./phantomjs.exe')
        self.save_path = save_path
        pass

    # 分析新浪汽车车型主页
    def analysis_main_page(self):
        self.driver.get(self.main_page)
        main_page = self.driver.page_source
        selector = etree.HTML(main_page)
        hrefs = selector.xpath('//dt/a/@href')
        names = selector.xpath('//dt/a/text()')

        # # 此处加入多线程写法
        # files = []
        # for h, n in zip(hrefs, names):
        #     files.append((h, n))
        #
        # with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        #     for _ in executor.map(self.sub_page, files):
        #         pass

        for i, (h, n) in enumerate(zip(hrefs, names)):
            print("the {} th page of main_list href:{}, name:{}".format(i, h, n))
            self.sub_page(h, n)

    # 解析二级分类
    # // db.auto.sina.com.cn/b76.html 阿尔法 - 罗密欧
    # // db.auto.sina.com.cn/b1.html 奥迪
    # // db.auto.sina.com.cn/b4.html 宝马
    def sub_page(self, h, n):
        sub_url = 'http:' + h
        path = os.path.join(self.save_path, n)
        self.make_dir(path)
        self.driver.get(sub_url)
        sub_page = self.driver.page_source
        selector = etree.HTML(sub_page)
        hrefs = selector.xpath('//div[@class="t fL"]/h2/a/@href')
        names = selector.xpath('//div[@class="t fL"]/h2/a/text()')
        for h, n in zip(hrefs, names):
            print(">>车型二级分类列表 href:{}, path:{}, name:{}".format(h, path, n))
            self.subsub_page(h, path, n)

    # 解析三级分类 对每个车的子系列进行分析
    def subsub_page(self, url, folder_path, name):
        sub_url = 'http:' + url
        path = os.path.join(folder_path, name)
        self.make_dir(path)
        self.driver.get(sub_url)
        sub_page = self.driver.page_source
        selector = etree.HTML(sub_page)
        images = selector.xpath('//li[@class="fL"]/div/a/img/@src')
        hrefs = selector.xpath('//li[@class="fL"]/p[@class="title"]/a/@href')
        names = selector.xpath('//li[@class="fL"]/p[@class="title"]/a/text()')
        # 爬取缩略图
        for i, h, n in zip(images, hrefs, names):
            print(">>>>车型三级分类列表 href:{}, path:{}, name:{}".format(h, path, n))
            self.subsubsub_page(h, path, n)

    # 详细的车页面 点击图片
    def subsubsub_page(self, url, folder_path, name):
        sub_url = 'http:' + url
        path = os.path.join(folder_path, name)
        self.make_dir(path)
        self.driver.get(sub_url)
        sub_page = self.driver.page_source
        selector = etree.HTML(sub_page)
        hrefs = selector.xpath('//*[@id="nav"]/ul/li[3]/a/@href')
        print(">>>>三级车车型详细页面:{}".format(hrefs[0]))
        self.search_year_type(hrefs[0], path)

    # 搜寻车的年份类型e.g. xxxx年xx款车型
    def search_year_type(self, url, folder_path, name=None):
        sub_url = 'http:' + url
        self.make_dir(folder_path)
        self.driver.get(sub_url)
        sub_page = self.driver.page_source
        selector = etree.HTML(sub_page)
        hrefs = selector.xpath('//dd[@class="in-p "]/a/@href')
        names = selector.xpath('//dd[@class="in-p "]/a/text()')
        for h, n in zip(hrefs, names):
            print(">>>>>>三级车型的年分类型href:{}, name:{}".format(h, n))
            self.select_type(h, folder_path, n)

    # 选择类型中的外观
    def select_type(self, url, folder_path, name):
        sub_url = 'http:' + url
        path = os.path.join(folder_path, name)
        self.make_dir(path)
        self.driver.get(sub_url)
        sub_page = self.driver.page_source
        selector = etree.HTML(sub_page)
        hrefs = selector.xpath('//*[@id="J_motoDataMain"]/div[1]/div[2]/div/ul/li[2]/dl/dd[2]/a/@href')
        print(">>>>>>三级车型中{}的外观".format(name, hrefs[0]))
        self.search_color(hrefs[0], path, name)

    # 搜寻颜色
    def search_color(self, url, folder_path, name=None):
        sub_url = 'http:' + url
        self.driver.get(sub_url)
        sub_page = self.driver.page_source
        selector = etree.HTML(sub_page)
        hrefs = selector.xpath('//*[@id="J_motoDataMain"]/div[1]/div[2]/div/ul/li[3]/dl/dd/a/@href')
        names = selector.xpath('//*[@id="J_motoDataMain"]/div[1]/div[2]/div/ul/li[3]/dl/dd/a/text()')
        for i, (h, n) in enumerate(zip(hrefs, names)):
            if i == 0:
                continue
            if re.match(r'javascript', h):
                continue
            print(">>>>>>>>三级车型{}外观第{}种颜色:{}, href:{}".format(name, i, n, h))
            self.search_high_image(h, folder_path, n)

    # 搜寻高清大图url
    def search_high_image(self, url, folder_path, name):
        sub_url = 'http:' + url
        path = os.path.join(folder_path, name)
        self.make_dir(path)
        self.driver.get(sub_url)
        sub_page = self.driver.page_source
        selector = etree.HTML(sub_page)
        hrefs = selector.xpath('//li[@class="fL"]/div/a/@href')
        for h in hrefs:
            # print(h)
            self.select_high_image(h, path)

    # 在大图的url中选择img.src 并下载
    def select_high_image(self, url, folder_path, name=None):
        sub_url = 'http:' + url
        self.driver.get(sub_url)
        sub_page = self.driver.page_source
        selector = etree.HTML(sub_page)
        hrefs = selector.xpath('/html/body/div[3]/div[1]/div[2]/div[1]/img/@src')
        print(sub_url, hrefs[0])

        # self.save_pic(hrefs[0], folder_path)

    def make_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def save_pic(self, url, save_path, timeout=30):
        try:
            print(">>>>>>>>>>download pic from {}, save path: {}".format(url, save_path))
            pic_name = str(time.time()) + '.jpg'
            file_path = os.path.join(save_path, pic_name)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            try:
                re_get = requests.get(url, timeout=timeout)
            except requests.exceptions.ConnectTimeout:
                print("connect time out")
            except requests.exceptions.Timeout:
                print("download time out")

            with open(file_path, "wb") as file:
                file.write(re_get.content)
        except Exception:
            print("download fail!")


sp = spider(main_page='http://db.auto.sina.com.cn/', save_path='./sina_download')
# sp.analysis_main_page()
# sp.sub_page('//db.auto.sina.com.cn/b76.html', '阿尔法-罗密欧')
# sp.subsub_page('//db.auto.sina.com.cn/p42.html', './download/阿尔法-罗密欧', '阿尔法-罗密欧')
# sp.subsubsub_page('//db.auto.sina.com.cn/2474/', './download/宝马/华晨宝马', '宝马2系旅行车')
# sp.search_year_type('//db.auto.sina.com.cn/photo/s2474.html',
#                     './download/宝马/华晨宝马/宝马2系旅行车')
# sp.select_type('//db.auto.sina.com.cn/photo/s2474-1-25504-1-0-0-1.html',
#                './download/宝马/华晨宝马/宝马2系旅行车',
#                '2016款宝马2系旅行车218i 1.5T自动时尚型')

# sp.search_color('//db.auto.sina.com.cn/photo/s2654-0-29496-1-1-9073-1.html',
#                 './download/阿尔法-罗密欧\阿尔法-罗密欧\Giulia\2017款Giulia 2.0T自动200HP豪华版')

# sp.search_high_image('//db.auto.sina.com.cn/photo/s2654-0-29496-1-1-9073-1.html',
#                 './download/阿尔法-罗密欧\阿尔法-罗密欧\Giulia\2017款Giulia 2.0T自动200HP豪华版',
#                 '蓝')
sp.select_high_image('//db.auto.sina.com.cn/photo/c91857-1-1-9073-0-1.html#129856992',
                     './download/宝马/华晨宝马/宝马2系旅行车/2016款宝马2系旅行车218i 1.5T自动时尚型/雪山白')
# sp = spider(main_page='http://db.auto.sina.com.cn/', save_path='./sina_download')
sp.select_high_image('//db.auto.sina.com.cn/photo/c91857-1-1-9073-0-1.html#129856993',
                     './download/宝马/华晨宝马/宝马2系旅行车/2016款宝马2系旅行车218i 1.5T自动时尚型/雪山白')
