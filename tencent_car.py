import requests
import re, os, time
from selenium import webdriver
from lxml import etree
import platform


# 有问题 腾讯汽车车型怕不下来 页面总是加载超时 不知道什么问题
class spider():
    def __init__(self, main_page, save_path):
        self.main_page = main_page
        self.save_path = save_path
        sys_type = platform.system()
        if sys_type == "Windows":
            # self.driver = webdriver.PhantomJS('./phantomjs.exe')
            self.driver = webdriver.Chrome('./chromedriver.exe')
        elif sys_type == "Linux":
            self.driver = webdriver.PhantomJS('/home1/fsb/env2/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
            # self.driver = webdriver.Firefox('/home1/fsb/env2/firefox/geckodriver')

    def analysis_main_page(self):
        select, path = self.get_selector_and_path(self.main_page, self.save_path, sleep=5)
        # containers = select.xpath('//brandlogo/div/a[2]/text()')
        if select is not None:
            containers = select.xpath('//div[@class="listAll"]')
            # main_names = select.xpath('//div[@class="listLogo"]/a[2]/text()')
            for i, container in enumerate(containers):
                # if i < 3:
                main_names = container.xpath('./brandlogo/div[@class="listLogo"]/a[2]/text()')
                print(main_names)
                for main_name in main_names:
                    names = container.xpath('./div[@class="listData"]/manname/h3/a/text()')
                    print(names)
                    listDatas = container.xpath('./div[@class="listData"]')
                    for name, listData in zip(names, listDatas):
                        sub_names = listData.xpath('./ul/li/a/text()')
                        print(sub_names)
                        hrefs = listData.xpath('./ul/li/a/@href')
                        for sub_name, href in zip(sub_names, hrefs):
                            path = os.path.join(self.save_path, main_name, name)
                            print(i, href, path, sub_name)
                            self.click_image(href, path, sub_name)
                            # time.sleep(0.1)

    def click_image(self, url, path, name):
        select, save_path = self.get_selector_and_path(url, path, name, sleep=0)
        if select is not None:
            hrefs = select.xpath('//li[@id="serial_pic"]/a/@href')
            if not len(hrefs) == 0:
                self.subsubsub_page(hrefs[0], save_path)

    def subsubsub_page(self, url, path, name=None):
        select, save_path = self.get_selector_and_path(url, path, name)
        if select is not None:
            hrefs = select.xpath('//div[@id="photo_list_wg"]/ul/li/a/@href')
            sub_names = select.xpath('//div[@id="photo_list_wg"]/ul/li/h4/text()')
            if hrefs is not None and sub_names is not None:
                for href, sub_name in zip(hrefs, sub_names):
                    print("--->", href, sub_name)
                    self.large_scale_image(href, save_path, sub_name)

    def large_scale_image(self, url, path, name):
        sub_url = url
        if not name is None:
            save_path = os.path.join(path, name)
        else:
            save_path = path
        self.make_dir(path)
        try:
            self.driver.set_page_load_timeout(10000)
            sys_type = platform.system()
            if sys_type == "Windows":
                # self.driver = webdriver.PhantomJS('./phantomjs.exe')
                self.driver = webdriver.Chrome('./chromedriver.exe')
            elif sys_type == "Linux":
                self.driver = webdriver.PhantomJS('/home1/fsb/env2/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
            self.driver.get(sub_url)
        except:
            print("\033[31;0m[URL ERROR] TIME_OUT\033[0m")
            return
        time.sleep(1)
        sub_page = self.driver.page_source
        select = etree.HTML(sub_page)
        if select is not None:
            hrefs = select.xpath('//img[@id="PicSrc"]/@src')
            if not len(hrefs) == 0:
                self.save_pic(hrefs[0], save_path)

    def get_selector_and_path(self, url, save_path, name=None, sleep=1):
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

            re_get = requests.get(url, timeout=timeout)
            time.sleep(1)
            with open(file_path, "wb") as file:
                file.write(re_get.content)
        except Exception:
            print("download fail!")


if __name__ == "__main__":
    sp = spider('http://data.auto.qq.com/car_brand/index.shtml', './tencent_download')
    sp.analysis_main_page()
    # sp.subsubsub_page('http://data.auto.qq.com/car_serial/1545' + '/serialpic_nl.shtml', './tencent_download\AC Schnitzer', ' AC Schnitzer M3')
    # sp.large_scale_iamge('http://data.auto.qq.com/car_public/1/disp_pic_nl.shtml#sid=1545&tid=1&pid=1930524',
    #                      './qq_download\AC Schnitzer\AC Schnitzer M3', '亚琛施纳泽 M3 资料图')
