import requests
import re, os, time
from selenium import webdriver
from lxml import etree


class spider():
    def __init__(self, main_page, save_path):
        self.main_page = main_page
        self.save_path = save_path
        self.driver = webdriver.PhantomJS('./phantomjs.exe')
        # self.driver = webdriver.Chrome('./chromedriver.exe')

    def analysis_main_page(self):
        select, path = self.get_selector_and_path(self.main_page, self.save_path)
        # containers = select.xpath('//brandlogo/div/a[2]/text()')
        hrefs = select.xpath('//div[@class="brand_name"]/h2/a/@href')
        names = select.xpath('//div[@class="brand_name"]/h2/a/@title')
        print(len(hrefs))
        for i, (name, href) in enumerate(zip(names, hrefs)):
            print(i, name, href)

    def sub_page(self, url, path, name):
        pass



    def get_selector_and_path(self, url, save_path, name=None):
        sub_url = url
        if not name is None:
            path = os.path.join(save_path, name)
        else:
            path = save_path
        self.make_dir(path)
        self.driver.get(sub_url)
        sub_page = self.driver.page_source
        selector = etree.HTML(sub_page)
        return selector, path

    def make_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def save_pic(self, url, save_path, timeout=30):
        try:
            print("--------->download pic from {}, save path: {}".format(url, save_path))
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


if __name__ == "__main__":
    sp = spider('http://product.auto.163.com/', './163_download')
    # sp.analysis_main_page()
    sp.sub_page()