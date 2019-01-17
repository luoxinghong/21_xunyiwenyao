# -*- coding: utf-8 -*-
import requests
from lxml import etree
import re


def parse_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko)   Chrome/62.0.3202.94 Safari/537.36",
    }
    html = requests.get(url, headers=headers).content
    return html.decode("GBK", "ignore")


def get_page_number(url):
    end_page_url = etree.HTML(parse_url(url)).xpath("//a[contains(text(),'尾页')]/@href")[0]
    html = parse_url(end_page_url)
    number = int(etree.HTML(html).xpath("//li[@class='thisclass']/text()")[0])
    return number


def parse_one_page(number):
    for i in range(1, number + 1):
        html = parse_url("http://www.xywy.com/wemedia/list_13460_{}.html".format(i))
        print("http://www.xywy.com/wemedia/list_13460_{}.html".format(i))
        print("*"*100)
        title_list = etree.HTML(html).xpath(
            "//ul[@class='pt15 f14 deepgray-a normal-a pub-txtlist pub-txtlistd']/li/a/text()")
        date_list = etree.HTML(html).xpath(
            "//ul[@class='pt15 f14 deepgray-a normal-a pub-txtlist pub-txtlistd']/li/span/text()")
        url_list = etree.HTML(html).xpath(
            "//ul[@class='pt15 f14 deepgray-a normal-a pub-txtlist pub-txtlistd']/li/a/@href")
        for j, k in enumerate(url_list):
            try:
                title = title_list[j]
                rstr = r"[\/\\\:\*\?\"\<\>\|\t]"
                title = re.sub(rstr, "-", title)
                date = date_list[j]
                html = parse_url(k)
                content = etree.HTML(html).xpath("//div[@class='artical']//text()")
                with open("./保健频道/" + date + '-' + title + '.txt', "w", encoding="utf-8") as f:
                    for l in content:
                        f.write(l.strip())
                    f.close()
                    print(date + '-' + title + '.txt' + " is save ok")
            except Exception as e:
                print(e,k)
            continue


if __name__ == '__main__':
    url = "http://www.xywy.com/wemedia/list_13460_1.html"
    number = get_page_number(url)
    parse_one_page(number)
