# encoding=utf-8
import requests
from urllib import request
import urllib.request
import socket, re, os, time
import urllib.error
from selenium import webdriver


# 一共267个车型


class crawlCar(object):
    def __init__(self):
        self.driver = webdriver.PhantomJS(executable_path='phantomjs.exe')
        self.source_page = 'https://car.autohome.com.cn'
        self.source_folder = './download'
        self.start()
        # self.main_page()
        # self.sub_page('https://car.autohome.com.cn/pic/brand-33.html', './download/奥迪')
        # self.analyse_subsub_page()
        # self.subsub_page()
        # self.analyse_subsubsub_page()
        # self.subsubsub_page()
        # self.get_scale_image()

    # Output:
    # 二级url目录:https://car.autohome.com.cn/pic/brand-14.html
    # 二级文件目录:./download\本田
    def start(self):
        main_list = self.main_page()
        for i, ml in enumerate(main_list):
            if i >= 155 and i < 200:
                sub_url_path = ml[0]
                sub_name = ml[1]
                sub_path = os.path.join(self.source_folder, sub_name)  # ./download/ABT
                if not os.path.exists(sub_path):
                    os.makedirs(sub_path)
                sub_url = self.source_page + sub_url_path
                print("第 {} 个, 二级url目录:{}, 二级文件目录:{}".format(i, sub_url, sub_path))
                self.sub_page(sub_url, sub_path)

    # d = ('/pic/brand-134.html', 'ABT')
    def main_page(self):
        # main_url = 'https://car.autohome.com.cn/pic/'
        # self.driver.get(main_url)
        # html = self.driver.page_source
        # main_match = '<li id=".*?<a href="(.*?)">.*?</i>"(.*?)"<em>.*?</em></a></h3></li>'
        # main_groups = re.findall(main_match, html)
        # for mg in main_groups:
        #     print(mg)

        with open('main_html.txt', encoding='utf-8') as f:
            html = f.read()

        href_match = 'href="(.*?)"'
        name_match = '</i>(.*?)<em>'
        href_groups = re.findall(href_match, html)
        name_groups = re.findall(name_match, html)

        main_list = []
        for href, name in zip(href_groups, name_groups):
            d = (href, name)
            main_list.append(d)
        # print(main_list)
        return main_list

    def sub_page(self, url, path):
        sub_url = url
        self.driver.get(sub_url)
        sub_html = self.driver.page_source
        sub_html_match = '<div class="row"><div class="column grid-16">' \
                         '.*?<a href="/pic/.*?" target="_blank">(.*?)</a>(.*?)</div></div>'
        sub_html_groups = re.findall(sub_html_match, sub_html)
        sub_box_match = '<li><a href="(.*?)"><img src="(.*?)".*?<a href=.*?>(.*?)</a>.*?</li>'
        for shg in sub_html_groups:

            # 创建二级文件目录
            sub_name = shg[0]
            sub_path = os.path.join(path, sub_name)
            if not os.path.exists(sub_path):
                os.makedirs(sub_path)

            sub_box_html = shg[1]
            sub_box_groups = re.findall(sub_box_match, sub_box_html)

            # 在二级文件中查找三级
            for sbg in sub_box_groups:
                subsub_url = sbg[0]
                subsub_pic = sbg[1]
                subsub_name = sbg[2]

                # 创建三级目录
                subsub_path = os.path.join(sub_path, subsub_name)
                self.save_pic('https:' + subsub_pic, subsub_path)  # 保存封面照片到三级文件目录

                # 三级url传入下一个函数
                subsub_url = self.source_page + subsub_url
                self.subsub_page(subsub_url, subsub_path)
                self.analyse_subsub_page(subsub_url, subsub_path)

    # 进入三级类型(e.g. 东风本田 杰德)页面:
    # 判断是否有停产车型
    # 有则在停产页面进行爬取, 无则返回None
    def analyse_subsub_page(self, url=None, path=None):
        # subsub_url = 'https://car.autohome.com.cn/pic/series/3104.html#pvareaid=2042214'
        subsub_url = url
        self.driver.get(subsub_url)
        subsub_html = self.driver.page_source
        stop_sale_match = '<span class="fn-right"><a href="(.*?)">(.*?)&nbsp.*?</a>'
        stop_sale_groups = re.findall(stop_sale_match, subsub_html)
        # 判断是否有停产车型页面 有则进入停产车型页面抓取 无则在本页面抓取
        if not stop_sale_groups.__len__() == 0:
            for ssg in stop_sale_groups:
                stop_sale_url = ssg[0]
                stop_sale_url = self.source_page + stop_sale_url
                self.subsub_page(stop_sale_url, path, False)

    # 在此页面需要 爬取车辆相关信息(要判断是否停产) 对车身外观 中控方向盘 车厢座椅子页面进行爬取
    # Input: issale: 是否在售?
    def subsub_page(self, url=None, path=None, issale=True):
        # subsub_url = 'https://car.autohome.com.cn/pic/series/3104.html#pvareaid=2042214'
        subsub_url = url
        self.driver.get(subsub_url)
        subsub_html = self.driver.page_source
        subsubsub_class_name_match = '<div class="uibox-title"><a href="(.*?)">(.*?)</a>'  # 三级车型下面的分类 对车身外观 中控方向盘 车厢座椅子
        subsubsub_class_name_groups = re.findall(subsubsub_class_name_match, subsub_html)
        # class_list =  ['车身外观', '中控方向盘', '车厢座椅', '其它细节', '评测', '重要特点', '活动']
        # class_list = ['车身外观', '中控方向盘', '车厢座椅', '其它细节', '评测']
        class_list = ['车身外观']
        # print(subsubsub_class_url_groups)
        # print(
        #     subsubsub_class_name_groups)  # [('/pic/series/3104-1.html#pvareaid=2042222', '车身外观'), ('/pic/series/3104-10.html#pvareaid=2042222', '中控方向盘'), ('/pic/series/3104-3.html#pvareaid=2042222', '车厢座椅'), ('/pic/series/3104-12.html#pvareaid=2042222', '其它细节'), ('/pic/series/3104-13.html#pvareaid=2042222', '评测'), ('/pic/series/3104-14.html#pvareaid=2042222', '重要特点'), ('/pic/series/3104-15.html#pvareaid=2042222', '活动')]
        for ssscng in subsubsub_class_name_groups:
            if ssscng[1] in class_list:
                subsubsub_url = ssscng[0]
                subsubsub_name = ssscng[1]  # 车身外观 等...
                if issale:
                    subsubsub_path = path
                else:
                    subsubsub_path = path + '(stop sale)'
                # if not os.path.exists(subsubsub_path):
                #     os.makedirs(subsubsub_path)

                # 传入下一个函数
                subsubsub_url = self.source_page + subsubsub_url
                self.subsubsub_page(subsubsub_url, subsubsub_path, subsubsub_name)
                self.analyse_subsubsub_page(subsubsub_url, subsubsub_path, subsubsub_name)

    # 进入(车身外观 中控方向盘 车厢座椅子) 需要判断是否有翻页
    def analyse_subsubsub_page(self, url=None, path=None, ex_path=None):
        # subsubsub_url = 'https://car.autohome.com.cn/pic/series/16-1.html'
        subsubsub_url = url
        self.driver.get(subsubsub_url)
        subsubsub_html = self.driver.page_source
        next_page_match = '<div class="page">.*?<a href="(.*?)">(.*?)</a>'
        next_page_groups = re.findall(next_page_match, subsubsub_html)  # [('/pic/series/16-1-p2.html', '2')]
        # print(next_page_groups)
        if not next_page_groups.__len__() == 0:
            for npg in next_page_groups:
                next_page_url = self.source_page + npg[0]
                self.subsubsub_page(next_page_url, path, ex_path)

    # 车身外观
    def subsubsub_page(self, url=None, path='./', ex_path=None):
        # subsubsub_url = 'https://car.autohome.com.cn/pic/series/3104-10.html'
        subsubsub_url = url
        self.driver.get(subsubsub_url)
        subsubsub_html = self.driver.page_source
        # pic_match = '<div class="uibox-con carpic-list03 border-b-solid"><ul><li>(.*?)</li>'
        pic_match = '<li><a href="(.*?)" title="(.*?)" target="_blank"><img src="(.*?)".*?</li>'
        pic_groups = re.findall(pic_match, subsubsub_html)
        # print(pic_groups)
        for pg in pic_groups:
            subsubsubsub_url = pg[0]
            subsubsubsub_name = pg[1]
            subsubsubsub_img = pg[2]
            subsubsubsub_path = os.path.join(path, subsubsubsub_name, ex_path)
            if not os.path.join(subsubsubsub_path):
                os.makedirs(subsubsubsub_path)
            # print(subsubsubsub_url, subsubsubsub_path)
            subsubsubsub_url = self.source_page + subsubsubsub_url
            self.get_scale_image(subsubsubsub_url, subsubsubsub_path)
            # subsubsubsub_img_url = 'https:' + subsubsubsub_img
            # self.save_pic(subsubsubsub_img_url, subsubsubsub_path)

    def get_scale_image(self, url=None, path=None):
        # image_url = 'https://car.autohome.com.cn/photo/25893/1/3415937.html#pvareaid=2042264'
        image_url = url
        self.driver.get(image_url)
        image_html = self.driver.page_source
        image_match = '<img id="img" src="(.*?)".*?'
        image_groups = re.findall(image_match, image_html)
        if not image_groups.__len__() == 0:
            self.save_pic('https:' + image_groups[0], path)

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


if __name__ == '__main__':
    car = crawlCar()
    # url = 'https://car2.autoimg.cn/cardfs/product/g6/M13/2B/0F/t_autohomecar__wKgH3FoBhP6AAhdSAAwAauwb4XE847.jpg'
    # car.save_pic(url, './')
