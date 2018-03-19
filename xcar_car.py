# encoding=utf-8
import requests
import re, os, time
from selenium import webdriver
from lxml import etree


class spider():
    def __init__(self, main_page, save_path):
        self.main_page = main_page
        self.save_path = save_path
        self.driver = webdriver.PhantomJS('./phantomjs.exe')

    # 分析主页面 一共164个
    def analysis_main_page(self):
        selector, path = self.get_selector_and_path(self.main_page, self.save_path)
        hrefs = selector.xpath('//div[@class="brand_col"]/div/ul/li/a/@href')
        names = selector.xpath('//div[@class="brand_col"]/div/ul/li/a/text()')
        for i, (href, name) in enumerate(zip(hrefs, names)):
            # if i == 80:
                print("第 {} 个车型, 下载地址：{}， 名字：{}".format(i, href, name))
                # self.sub_page(href, path, name)

    # 分析二级类型及其三级类型
    def sub_page(self, url, folder_path, name):
        selector, path = self.get_selector_and_path(url, folder_path, name)
        # sub_names = selector.xpath('//div[@class="choose_wrap mt10 clearfix"]/div[@class="design"]/a/text()')
        blocks = selector.xpath('//div[@class="brand_right"]/div[@class="choose_wrap mt10 clearfix"]')
        for block in blocks:
            sub_name = block.xpath('./div[@class="design"]/a/text()')
            print("--->二级车型名字:{}".format(sub_name))
            sub_path = path + '/' + sub_name[0]
            self.make_dir(sub_path)
            hrefs = block.xpath('./div[@class="car_list"]/div/a/@href')
            subsub_names = block.xpath('./div[@class="car_list"]/div/a/img/@title')
            for (href, subsub_name) in zip(hrefs, subsub_names):
                print("------->三级车型名字：{}, href: {}".format(subsub_name, href))
                self.subsubsub_page(self.main_page + href, sub_path, subsub_name)

    # 进入三级页面的一些点击
    def subsubsub_page(self, url, folder_path, name):
        selector, path = self.get_selector_and_path(url, folder_path, name)
        hrefs = selector.xpath('//div[@class="brand_right"]/div/div[@class="data_main"]/div[@class="data_img"]/a/@href')
        selector, path = self.get_selector_and_path(self.main_page + hrefs[0], path, None)
        hrefs = selector.xpath('//*[@id="photo_lazyload"]/div[1]/span[2]/a/@href')
        # 如果没有实物照片 返回
        if len(hrefs) == 0:
            return
        selector, path = self.get_selector_and_path(self.main_page + hrefs[0], path, None)
        hrefs = selector.xpath(
            '//div[@class="atlas_right"]/div[@class="pic-wrap"]/div[@class="pic-head"]/span[2]/a/@href')
        # 进入详细的页面， 查找翻页
        selector, path = self.get_selector_and_path(self.main_page + hrefs[0], path, None)
        pages_hrefs = selector.xpath('//div[@class="sort-page"]/a/@href')

        # 如果没有更多
        if len(pages_hrefs) != 0:
            for href in pages_hrefs:
                self.analysis_pages(self.main_page + href, path, None)
        else:
            self.analysis_pages(self.main_page + hrefs[0], path, None)

    def analysis_pages(self, url, folder_path, name):
        selector, path = self.get_selector_and_path(url, folder_path, name)
        hrefs = selector.xpath('//dl/dt/a/@href')
        ssssub_names = selector.xpath('//dl/dd/span/a/text()')
        for href, ssssb_name in zip(hrefs, ssssub_names):
            self.large_scale_iamge(self.main_page + href, path, ssssb_name)

    def large_scale_iamge(self, url, folder_path, name):
        selector, path = self.get_selector_and_path(url, folder_path, name)
        hrefs = selector.xpath('//div[@class="picture_main"]/div[1]/div[1]/ul/li/img/@src')
        self.save_pic(hrefs[0], path)

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
    sp = spider('http://newcar.xcar.com.cn', './xcar_path')
    sp.analysis_main_page()
    # sp.sub_page('http://newcar.xcar.com.cn/car/0-0-0-0-1-0-0-0-0-0-0-0/', './xcar_path', '奥迪')
    # sp.subsubsub_page('http://newcar.xcar.com.cn/car/select/s2365/', './xcar_path/奥迪', '奥迪A3两厢')
    # sp.analysis_pages('http://newcar.xcar.com.cn/photo/ps2365-s_1/?page=1', './xcar_path/奥迪/奥迪A3两厢', None)
    # sp.large_scale_iamge('http://newcar.xcar.com.cn/photo/s9541_1/3638346.htm', './xcar_path/奥迪/奥迪A3两厢',
    #                      '2018款30周年版 Sportback 35 TFSI进取型')
