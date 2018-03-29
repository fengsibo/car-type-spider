import requests
import re, os, time
from selenium import webdriver
from lxml import etree
from selenium.webdriver.support.select import Select


class spider():
    def __init__(self, main_page, save_path):
        self.main_page = main_page
        self.save_path = save_path
        # self.driver = webdriver.PhantomJS('./phantomjs.exe')
        self.driver = webdriver.Chrome('./chromedriver.exe')

    def analysis_main_page(self):
        select, path = self.get_selector_and_path(self.main_page, self.save_path)
        # containers = select.xpath('//brandlogo/div/a[2]/text()')
        hrefs = select.xpath('//div[@class="brand_name"]/h2/a/@href')
        names = select.xpath('//div[@class="brand_name"]/h2/a/@title')
        print(len(hrefs))
        for i, (name, href) in enumerate(zip(names, hrefs)):
            print(i, name, href)
            self.sub_page(href, path, name)

    def sub_page(self, url, path, name=None):
        selector, save_path = self.get_selector_and_path(self.main_page + url, path, name)
        containers = selector.xpath('//div[@class="c-bd"]/div[1]')
        for container in containers:
            blocks = container.xpath('./div')
            sub_names = container.xpath('./div/p/text()')
            for block, sub_name in zip(blocks, sub_names):
                items = block.xpath('./ul/li')
                for item in items:
                    subsub_names = item.xpath('./p[@class="title"]/a/text()')
                    hrefs = item.xpath('./p[@class="photo"]/a/@href')
                    new_path = os.path.join(save_path, sub_name)
                    for subsub_name, href in zip(subsub_names, hrefs):
                        # print(subsub_name, href, new_path)
                        self.click_all_image(href, new_path, subsub_name)

    # 点击 全部图片
    def click_all_image(self, url, path, name=None):
        selector, save_path = self.get_selector_and_path(self.main_page + url, path, name)
        hrefs = selector.xpath('//div[@class="status"]/a/@href')
        if not len(hrefs) == 0:
            self.select_years(hrefs[0], save_path)

    def select_years(self, url, path, name=None):
        selector, save_path = self.get_selector_and_path(self.main_page + url, path, name)
        option_values = selector.xpath('//select[@id="yeartype_select"]/option/@value')
        if not len(option_values) == 0:
            for option_value in option_values:
                self.driver.get(self.main_page + url)
                option_years = Select(self.driver.find_element_by_id('yeartype_select'))
                option_years.select_by_value(option_value)  # 容易导致元素链接失败
                time.sleep(0.1)
                year_url = self.driver.current_url
                self.select_type(year_url, save_path, option_value)

    # 选择汽车类型
    def select_type(self, url, path, name=None):
        selector, save_path = self.get_selector_and_path(url, path, name)
        option_values = selector.xpath('//select[@id="autoproduct_select"]/option/@value')
        option_names = selector.xpath('//select[@id="autoproduct_select"]/option/text()')
        if not len(option_values) == 0:
            for option_value, option_name in zip(option_values, option_names[1:]):
                self.driver.get(url)
                option_types = Select(self.driver.find_element_by_id('autoproduct_select'))
                option_types.select_by_value(option_value)
                time.sleep(0.25)
                print("---->", self.driver.current_url, option_name)
                self.subsub_page(self.driver.current_url, save_path, option_name)

    def subsub_page(self, url, path, name=None):
        selector, save_path = self.get_selector_and_path(url, path, name)
        if selector is not None:
            directions = selector.xpath('//div[@class="bd"]/ul[@class="clearfix"]/li/a/h4/text()')
            hrefs = selector.xpath('//div[@class="bd"]/ul[@class="clearfix"]/li/a/@href')
            if not len(hrefs) == 0:
                for direction, href in zip(directions, hrefs):
                    if direction in ['左前', '正前', '正侧', '左后', '正后', '右后']:
                        self.large_scale_pic(href, save_path, direction)

    def large_scale_pic(self, url, path, name=None):
        selector, save_path = self.get_selector_and_path(url, path, name)
        # hrefs = selector.xpath('//img[@class="low_photo"]/@src')
        hrefs = selector.xpath('//img[@class="main_photo hidden"]/@src')
        if not len(hrefs) == 0:
            self.save_pic(hrefs[0], save_path)

    def get_selector_and_path(self, url, save_path, name=None, sleep=0):
        sub_url = url
        if not name is None:
            path = os.path.join(save_path, name)
        else:
            path = save_path
        self.make_dir(path)
        try:
            self.driver.set_page_load_timeout(10000)
            self.driver.get(sub_url)
        except:
            print("\033[31;0m[URL ERROR] TIME_OUT\033[0m")
            return None, path
        time.sleep(sleep)
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
    sp = spider('http://product.auto.163.com', './163_download')
    sp.analysis_main_page()
    # sp.sub_page('/new_daquan/brand/1685.html', './163_download/奥迪')
    # sp.click_all_image('/series/3148.html#new18list', './163_download/奥迪/一汽-大众奥迪', '奥迪Q5')
    # sp.subsub_page('/series/photo/3148.html#ncx00040', './163_download/奥迪/一汽-大众奥迪/奥迪Q5')
    # sp.large_scale_pic('http://product.auto.163.com/picture/photoview/2AF90008/193635/CQBHDQVT2AF90008.html',
    #                    './163_download/奥迪/一汽-大众奥迪/奥迪Q5')
