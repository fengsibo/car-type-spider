# qichezhijia-crawl
这是一个python爬虫项目， 目前有两个：
1.爬取汽车之家的车型图片数据，代码在qichezhijia_car.py，使用的是正则表达式方法
2.爬取新浪汽车的车型图片数据，代码在sina_car.py，使用的是xpath方法

说明：
1.运行环境在windows下，如在别的系统跑把driver换一下即可
2.可能用不了多线程，由于变量共享，文件夹会创建错误，sina_car.py中analysis_main_page()函数给出了多线程的写法
3.下载时间超过30s设为超时，可以在save_pic函数中timeout参数自行更改
4.下载速度不能太快，会被对方服务器发现，发出拦截，实在控制不了在每个调用save_pic()后面加上sleep()函数可以解决
