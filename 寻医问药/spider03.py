# coding=utf-8
import requests
import re
from lxml import etree
import os
import shutil

requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数


class spider(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "Connection": "close",
        }

    def parse_url(self, url):
        try:
            html = requests.get(url, headers=self.headers).content.decode("GBK", "ignore")
        except Exception as e:
            print(url, e)
            html = ''
        finally:
            return html

    # 按部位保存疾病和页面
    def get_body_part_jibing(self, url_list, name_list):
        for i, url in enumerate(url_list):
            html = self.parse_url(url)
            with open("./疾病/部位/html/" + str(i + 1) + name_list[i] + "_疾病页面.txt", "w") as f:
                f.write(html)
                f.close()
            content = etree.HTML(html)
            list = content.xpath("//ul[@class = 'ks-ill-list clearfix mt10']/li/a/@title")
            list = sorted(set(list), key=list.index)
            with open("./疾病/部位/txt/" + str(i + 1) + name_list[i] + "_疾病.txt", "w") as f:
                for j in list:
                    f.write(j.strip() + "\n")
                f.close()

    # 按部位保存症状和页面
    def get_body_part_zhengzhuang(self, url_list, name_list):
        for i, url in enumerate(url_list):
            html = self.parse_url(url)
            with open("./症状/部位/html/" + str(i + 1) + name_list[i] + "_症状页面.txt", "w") as f:
                f.write(html)
                f.close()
            content = etree.HTML(html)
            list = content.xpath("//ul[@class = 'ks-ill-list clearfix mt10']/li/a/@title")
            list = sorted(set(list), key=list.index)
            with open("./症状/部位/txt/" + str(i + 1) + name_list[i] + "_症状.txt", "w") as f:
                for j in list:
                    f.write(j.strip() + "\n")
                f.close()

    # 按字母保存疾病和详情页面,同时按字母抓取疾病页里的介绍、问答、文章
    def get_character_jibing(self, url_list, name_list):
        # 获取每个字母包含的疾病，保存到txt
        for i, url in enumerate(url_list):
            html = self.parse_url(url)
            with open("./疾病/字母/html/" + name_list[i] + "_疾病页面.html", "w") as f:
                f.write(html)
                f.close()
            content = etree.HTML(html)
            list = content.xpath("//ul[@class = 'ks-zm-list clearfix mt10']/li/a/text()")
            one_page_url_list = content.xpath("//ul[@class = 'ks-zm-list clearfix mt10']/li/a/@href")
            namelist = []
            for j in list:
                if j.endswith("."):
                    # 获取省略了疾病名称的url地址，但是会出现一个页面两个省略疾病名称相同的情况
                    xpath0 = "//ul[@class = 'ks-zm-list clearfix mt10']/li/a[text()='{}']/@href".format(j)
                    temp_url = content.xpath(xpath0)[0]
                    html = requests.get("http://jib.xywy.com" + temp_url).content
                    name = etree.HTML(html).xpath("//div[@class='jb-name fYaHei gre']/text()")[0]
                    namelist.append(name.strip())
                else:
                    namelist.append(j.strip())
            with open("./疾病/字母/txt/" + name_list[i] + "_疾病.txt", "w") as f:
                for k in namelist:
                    f.write(k + "\n")
                f.close()
            print("①获取字母{}包含的疾病，保存text成功".format(name_list[i]))

            # 获取每个疾病的详情页地址，提取疾病介绍
            for l, url in enumerate(one_page_url_list):
                try:
                    postfix = url.split("_")[-1]
                    # 进入疾病详情页
                    url = "http://jib.xywy.com/il_sii/cause/" + postfix
                    html = self.parse_url(url)
                    # 获取疾病介绍的各个标题
                    title = etree.HTML(html).xpath("//div[@class='jib-nav fl bor']//li/a/text()")
                    title = [t for t in title if t != "图说疾病"]
                    # 获取各标题对应的url
                    total_url = etree.HTML(html).xpath("//div[@class='jib-nav fl bor']//li/a/@href")
                    total_url = [url for url in total_url if "tushuojibing" not in url]
                    # 保存疾病介绍
                    rstr = r"[\/\\\:\*\?\"\<\>\|]"
                    name_temp = re.sub(rstr, "_", namelist[l])
                    if name_temp not in os.listdir('./疾病/details'):
                        os.mkdir('./疾病/details/' + name_temp)
                    else:
                        shutil.rmtree('./疾病/details/' + name_temp)
                        os.mkdir('./疾病/details/' + name_temp)
                    with open('./疾病/details/' + name_temp + '/' + name_temp + "_介绍.txt",
                              "w", encoding="utf-8") as f:
                        for m, u in enumerate(total_url):
                            f.write(title[m] + "：" + "\n")
                            html = self.parse_url("http://jib.xywy.com" + u)
                            text = etree.HTML(html).xpath(
                                "//div[@class='jib-articl fr f14 ']//*//text()|//div[@class='jib-articl fr f14 jib-lh-articl']//*//text()|//div[@class=' jib-articl fr f14 jib-lh-articl']//*//text()")
                            for t in text:
                                if len(t) > 0:
                                    f.write(t.strip())
                            f.write("\n" + "\n")
                        f.close()
                    print("②" + name_temp + "____疾病介绍保存成功")

                    # 提取医生解答
                    url_answer = url.replace("cause", "answer")
                    html = self.parse_url(url_answer)
                    answer_title_list = etree.HTML(html).xpath("//p[@class='fl pub-ask-da f14']//a/text()")
                    answer_url_list = etree.HTML(html).xpath("//p[@class='fl pub-ask-da f14']//a/@href")
                    for m, n in enumerate(answer_url_list):
                        try:
                            if not n.startswith("http"):
                                n = "http://jib.xywy.com" + n
                            html = self.parse_url(n)
                            # 问题详情页对应的xpath不同，有的直接跳到疾病介绍或者病因，有的是常见问题
                            # 正常问题详情页
                            question = etree.HTML(html).xpath("//div[@class='graydeep User_quecol pt10 mt10']//text()")
                            # 问题介绍、病因什么的
                            if len(question) == 0:
                                answer = etree.HTML(html).xpath(
                                    "//div[@class='jib-articl fr f14']//text()|//div[@class='jib-articl fr f14 ']//text()|//div[@class='jib-articl fr f14 jib-lh-articl']//text()|//div[@class=' jib-articl fr f14 jib-lh-articl']//text()")
                                question = [""]
                            else:
                                answer = etree.HTML(html).xpath(
                                    "//div[@class='pt15 f14 graydeep  pl20 pr20 deepblue']//text()|//div[@class='f14 btn-a lh180']//text()")
                            with open('./疾病/details/' + name_temp + '/' + name_temp + "_解答.txt", "a",
                                      encoding="utf-8") as f:
                                f.write('问题标题：' + answer_title_list[m] + '\n')
                                question_contnet = (''.join(question)).strip()
                                f.write('问题内容：' + question_contnet.replace('\n', '') + '\n')
                                # answer_str = (''.join(answer)).strip()
                                answer_str = [s.strip() for s in answer]
                                answer_str = (''.join(answer)).strip()
                                f.write('问题回答：' + answer_str.replace('\n', '') + '\n' + "\n")
                                f.close()
                        except Exception as e:
                            print(e)
                        continue
                    print("③" + name_temp + "____疾病解答保存成功")

                    # 获取疾病的相关文章
                    prefix_url_list = ["http://jib.xywy.com/il_sii/article_cause/",
                                       "http://jib.xywy.com/il_sii/article_symptom/",
                                       "http://jib.xywy.com/il_sii/article_treat/",
                                       "http://jib.xywy.com/il_sii/article_inspect/",
                                       "http://jib.xywy.com/il_sii/article_prevent/",
                                       "http://jib.xywy.com/il_sii/article_food/"]
                    with open('./疾病/details/' + name_temp + '/' + name_temp + "_文章.txt", "w", encoding="utf-8") as f:
                        for prefix_url in prefix_url_list:
                            try:
                                url_article = prefix_url + postfix
                                html = self.parse_url(url_article)
                                # 获取相关文章的各小分类[病因、症状、治疗、、、]
                                all_url = etree.HTML(html).xpath(
                                    "//div[@class='jib-expert-articl fr ']/div/p[1]/a/@href|//div[@class='jib-expert-articl fr']/div/p[1]/a/@href")
                                all_name = etree.HTML(html).xpath(
                                    "//div[@class='jib-expert-articl fr ']/div/p[1]/a/text()|//div[@class='jib-expert-articl fr']/div/p[1]/a/text()")
                                for p, q in enumerate(all_url):
                                    if not q.startswith("http"):
                                        q = "http://jib.xywy.com" + q
                                    h = self.parse_url(q)
                                    content = etree.HTML(h).xpath(
                                        "//div[@class=' jib-articl fr f14 jib-lh-articl']//text()|//div[@class='jib-articl fr f14 jib-lh-articl']//text()|//div[@class='jib-articl fr f14']//text()|//div[@class='new_artcont pt10 f14 lh180 clearfix']//text()|//div[@class='artical']//text()|//div[@class='passage pl10 pr10 f14']//text()|//div[@class='content']//text()|//div[@class='jib-articl fr f14 ']//text()")
                                    f.write("文章标题：" + all_name[p] + "\n")
                                    content = [s.strip() for s in content]
                                    content = ''.join(content)
                                    f.write("正文：" + content.replace('\n', '') + "\n" + "\n")
                            except Exception as e:
                                print(e)
                            continue
                        f.close()
                        print("④" + name_temp + "____疾病文章保存成功")
                        print("_" * 150)
                except Exception as e:
                    print(url, e)

    # 按字母保存症状和页面
    def get_character_zhengzhuang(self, url_list, name_list):
        # 访问以字母分页的症状页面
        for i, url in enumerate(url_list):
            html = self.parse_url(url)
            with open("./症状/字母/html/" + name_list[i] + "_症状页面.txt", "w") as f:
                f.write(html)
                f.close()
            content = etree.HTML(html)
            list = content.xpath(
                "//ul[@class = 'ks-zm-list clearfix']/li/a/text()|//ul[@class = 'ks-zm-list clearfix ']/li/a/text()")
            namelist = []
            for j in list:
                if j.endswith("."):
                    xpath0 = "//ul[@class = 'ks-zm-list clearfix']/li/a[text()='{}']/@title|//ul[@class = 'ks-zm-list clearfix ']/li/a[text()='{}']/@title".format(
                        j, j)
                    name = content.xpath(xpath0)[0]
                    namelist.append(name.strip())
                else:
                    namelist.append(j.strip())
            with open("./症状/字母/txt/" + name_list[i] + "_症状.txt", "w") as f:
                for k in namelist:
                    f.write(k + "\n")
                f.close()
            print("①获取字母{}包含的症状，保存text".format(name_list[i]))

            one_page_url_list = content.xpath("//div[@id='illA']//li/a/@href")
            one_page_url_list = [url.replace("gaishu", "jieshao") for url in one_page_url_list]
            # 获取每个症状的地址，提取症状介绍
            for l, url in enumerate(one_page_url_list):
                try:
                    url = ("http://zzk.xywy.com" + url).replace("gaishu", "jieshao")
                    html = self.parse_url(url)
                    # 获取症状介绍页标题
                    title = etree.HTML(html).xpath("//ul[@class='zz-nav-list clearfix']/li/a/text()")
                    total_url = etree.HTML(html).xpath("//ul[@class='zz-nav-list clearfix']/li/a/@href")
                    # 保存症状介绍
                    rstr = r"[\/\\\:\*\?\"\<\>\|]"
                    name_temp = re.sub(rstr, "_", namelist[l])
                    if name_temp not in os.listdir('./症状/details'):
                        os.mkdir('./症状/details/' + name_temp)
                    else:
                        shutil.rmtree('./症状/details/' + name_temp)
                        os.mkdir('./症状/details/' + name_temp)
                    with open('./症状/details/' + name_temp + '/' + name_temp + "_介绍.txt", "w", encoding="utf-8") as f:
                        for m, u in enumerate(total_url):
                            f.write(title[m] + "：" + "\n")
                            html = self.parse_url("http://zzk.xywy.com" + u)
                            text = etree.HTML(html).xpath(
                                "//div[@class='zz-articl fr f14']//*//text()|//div[@class='zz-articl fr f14 mt15']//*//text()")
                            for t in text:
                                if len(t) > 0:
                                    f.write(t.strip())
                            f.write("\n" + "\n")
                        f.close()
                    print("②" + name_temp + "症状介绍 is save ok")

                    # 提取医生解答
                    url_answer = url.replace("jieshao", "wenda")
                    s = self.parse_url(url_answer)
                    answer_title_list = etree.HTML(s).xpath("//div[@class='user-ask clearfix mt10 ']/p/a/text()")
                    answer_url_list = etree.HTML(s).xpath("//div[@class='user-ask clearfix mt10 ']/p/a/@href")
                    for x, y in enumerate(answer_url_list):
                        try:
                            if not y.startswith("http"):
                                y = "http://zzk.xywy.com" + y
                            html = self.parse_url(y)
                            question = etree.HTML(html).xpath("//div[@id='qdetailc']//text()")
                            if len(question) == 0:
                                answer = etree.HTML(html).xpath(
                                    "//div[@class='jib-articl fr f14']//text()|//div[@class='jib-articl fr f14 ']//text()|//div[@class='jib-articl fr f14 jib-lh-articl']//text()|//div[@class=' jib-articl fr f14 jib-lh-articl']//text()|//div[class='jib-articl fr f14 '//text()]")
                                question = ['']
                            else:
                                answer = etree.HTML(html).xpath(
                                    "//div[@class='pt15 f14 graydeep  pl20 pr20 deepblue']//text()|//div[@class='f14 btn-a lh180']//text()")

                            with open('./症状/details/' + name_temp + '/' + name_temp + "_解答.txt", "a",
                                      encoding="utf-8") as f:
                                f.write('问题标题：' + answer_title_list[x] + '\n')
                                question_contnet = (''.join(question)).strip()
                                f.write('问题内容：' + question_contnet.replace('\n', '') + '\n')
                                answer_str = (''.join(answer)).strip()
                                f.write('问题回答：' + answer_str.replace('\n', '') + '\n' + '\n')
                                f.close()
                        except Exception as e:
                            print(e)
                        continue
                    print("③" + name_temp + "____症状解答保存成功")

                    # 获取症状的相关文章
                    url = url.replace("jieshao", "zhishi")
                    html = self.parse_url(url)
                    url_article_list = etree.HTML(html).xpath("//div[@class='expert-articl bor']//p[1]/a/@href")
                    url_article_name_list = etree.HTML(html).xpath("//div[@class='expert-articl bor']//p[1]/a/text()")
                    with open('./症状/details/' + name_temp + '/' + name_temp + "_文章.txt", "w", encoding="utf-8") as f:
                        for p, q in enumerate(url_article_list):
                            try:
                                url_article = q
                                if not q.startswith("http"):
                                    url_article = "http://zzk.xywy.com" + q
                                html = self.parse_url(url_article)
                                content = etree.HTML(html).xpath("//div[@class='zz-articl fr f14']//text()|//div[@class='new_artcont pt10 f14 lh180 clearfix']//text()")
                                f.write("文章标题：" + url_article_name_list[p] + "\n")
                                content = [s.strip() for s in content]
                                content = ''.join(content)
                                f.write("正文：" + content.replace('\n', '') + "\n" + "\n")

                            except Exception as e:
                                print(e)
                            continue
                        f.close()
                        print("④" + name_temp + "____症状文章保存成功")
                        print("_" * 150)
                except Exception as e:
                    print(url, e)

    # 按科室保存疾病和页面
    def get_keshi_jibing(self, url_list, name_list):
        for i, url in enumerate(url_list):
            html = self.parse_url(url)
            with open("./疾病/科室/html/" + "{:0>2}".format(i) + name_list[i] + "_疾病页面.txt", "w") as f:
                f.write(html)
                f.close()
            content = etree.HTML(html)
            list = content.xpath("//ul[@class = 'ks-ill-list clearfix mt10']/li/a/text()")
            namelist = []
            for j in list:
                if j.endswith("."):
                    xpath0 = "//ul[@class = 'ks-ill-list clearfix mt10']/li/a[text()='{}']/@href".format(j)
                    temp_url = content.xpath(xpath0)[0]
                    html = requests.get("http://jib.xywy.com" + temp_url).content
                    name = etree.HTML(html).xpath("//div[@class='jb-name fYaHei gre']/text()")[0]
                    namelist.append(name.strip())
                else:
                    namelist.append(j.strip())
            namelist = sorted(set(namelist), key=namelist.index)
            with open("./疾病/科室/txt/" + "{:0>2}".format(i) + name_list[i] + "_疾病.txt", "w") as f:
                for k in namelist:
                    f.write(k.strip() + "\n")
                f.close()

        def get_character_zhengzhuang(self, url_list, name_list):
            # 访问以字母分页的症状页面
            for i, url in enumerate(url_list):
                html = self.parse_url(url)
                with open("./症状/字母/html/" + name_list[i] + "_症状页面.txt", "w") as f:
                    f.write(html)
                    f.close()
                content = etree.HTML(html)
                list = content.xpath(
                    "//ul[@class = 'ks-zm-list clearfix']/li/a/text()|//ul[@class = 'ks-zm-list clearfix ']/li/a/text()")
                namelist = []
                for j in list:
                    if j.endswith("."):
                        xpath0 = "//ul[@class = 'ks-zm-list clearfix']/li/a[text()='{}']/@title|//ul[@class = 'ks-zm-list clearfix ']/li/a[text()='{}']/@title".format(
                            j, j)
                        name = content.xpath(xpath0)[0]
                        namelist.append(name.strip())
                    else:
                        namelist.append(j.strip())
                with open("./症状/字母/txt/" + name_list[i] + "_症状.txt", "w") as f:
                    for k in namelist:
                        f.write(k + "\n")
                    f.close()

    # 按科室保存症状和页面
    def get_keshi_zhengzhuang(self, url_list, name_list):
        # 访问以科室分页的症状页面
        for i, url in enumerate(url_list):
            html = self.parse_url(url)
            with open("./症状/科室/html/" + "{:0>2}".format(i) + name_list[i] + "_症状页面.txt", "w") as f:
                f.write(html)
                f.close()
            content = etree.HTML(html)
            list = content.xpath("//ul[@class = 'ks-ill-list clearfix mt10']/li/a/@title")
            list = sorted(set(list), key=list.index)
            with open("./症状/科室/txt/" + "{:0>2}".format(i) + name_list[i] + "_症状.txt", "w") as f:
                for j in list:
                    f.write(j.strip() + "\n")
                f.close()


if __name__ == '__main__':
    # 疾病按部位分类需要的url和name
    jibing_buwei_url = ["http://jib.xywy.com/html/bi.html", "http://jib.xywy.com/html/er.html",
                        "http://jib.xywy.com/html/yan.html", "http://jib.xywy.com/html/kou.html",
                        "http://jib.xywy.com/html/jingbu.html", "http://jib.xywy.com/html/xiazhi.html",
                        "http://jib.xywy.com/html/shangzhi.html", "http://jib.xywy.com/html/xiongbu.html",
                        "http://jib.xywy.com/html/fubu.html", "http://jib.xywy.com/html/yaobu.html",
                        "http://jib.xywy.com/html/nvxingpengu.html", "http://jib.xywy.com/html/nanxinggugou.html",
                        "http://jib.xywy.com/html/pifu.html", "http://jib.xywy.com/html/quanshen.html",
                        "http://jib.xywy.com/html/paixiebuwei.html"]
    jibing_buwei_name = ["鼻", "耳", "眼", "口", "颈部", "下肢", "上肢", "胸部", "腹部", "腰部", "女性盆骨", "男性股沟", "皮肤", "全身", "排泄部位"]
    # 症状按部位分类需要的url和name
    zhengzhuang_buwei_url = ["http://zzk.xywy.com/p" + i[24:] for i in jibing_buwei_url]
    zhengzhuang_buwei_name = ["鼻", "耳", "眼", "口", "颈部", "下肢", "上肢", "胸部", "腹部", "腰部", "女性盆骨", "男性股沟", "皮肤", "全身",
                              "排泄部位"]

    # 按字母分类需要的url和name
    # jibing_character_url = ["http://jib.xywy.com/html/%s.html" % i for i in 'abcdefghijklmnpqrstuwxyz']
    # jibing_character_name = [i for i in 'abcdefghijklmnpqrstuwxyz']

    jibing_character_url = ["http://jib.xywy.com/html/%s.html" % i for i in 'lwxyz']
    jibing_character_name = [i for i in 'lwxyz']

    zhengzhuang_character_url = ["http://zzk.xywy.com/p/%s.html" % i for i in 'z']
    zhengzhuang_character_name = [i for i in 'z']

    # 疾病按科室分类需要的url和name
    jibing_keshi_url = ['http://jib.xywy.com/html/huxineike.html', 'http://jib.xywy.com/html/xiaohuaneike.html',
                        'http://jib.xywy.com/html/miniaoneike.html', 'http://jib.xywy.com/html/xinneike.html',
                        'http://jib.xywy.com/html/xueyeke.html', 'http://jib.xywy.com/html/neifenmike.html',
                        'http://jib.xywy.com/html/shenjingneike.html', 'http://jib.xywy.com/html/shenneike.html',
                        'http://jib.xywy.com/html/yichuanbingke.html', 'http://jib.xywy.com/html/fengshimianyike.html',
                        'http://jib.xywy.com/html/ganranke.html', 'http://jib.xywy.com/html/puwaike.html',
                        'http://jib.xywy.com/html/guwaike.html', 'http://jib.xywy.com/html/shenjingwaike.html',
                        'http://jib.xywy.com/html/xinxiongwaike.html', 'http://jib.xywy.com/html/gandanwaike.html',
                        'http://jib.xywy.com/html/miniaowaike.html', 'http://jib.xywy.com/html/shaoshangke.html',
                        'http://jib.xywy.com/html/gangchangke.html', 'http://jib.xywy.com/html/zhengxingmeirongke.html',
                        'http://jib.xywy.com/html/fuke.html', 'http://jib.xywy.com/html/chanke.html',
                        'http://jib.xywy.com/html/chuanranke.html', 'http://jib.xywy.com/html/buyunbuyu.html',
                        'http://jib.xywy.com/html/nanke.html', 'http://jib.xywy.com/html/pifuke.html',
                        'http://jib.xywy.com/html/xingbingke.html', 'http://jib.xywy.com/html/zhongyizonghe.html',
                        'http://jib.xywy.com/html/yanke.html', 'http://jib.xywy.com/html/kouqiangke.html',
                        'http://jib.xywy.com/html/erbihouke.html', 'http://jib.xywy.com/html/jingshenke.html',
                        'http://jib.xywy.com/html/xinlike.html', 'http://jib.xywy.com/html/erkezonghe.html',
                        'http://jib.xywy.com/html/xiaoerwaike.html', 'http://jib.xywy.com/html/xiaoerneike.html',
                        'http://jib.xywy.com/html/yingyangke.html', 'http://jib.xywy.com/html/zhongliuneike.html',
                        'http://jib.xywy.com/html/zhongliuwaike.html', 'http://jib.xywy.com/html/jianfei.html',
                        'http://jib.xywy.com/html/kangfuke.html', 'http://jib.xywy.com/html/qitazonghe.html',
                        'http://jib.xywy.com/html/jizhenke.html', 'http://jib.xywy.com/html/ganbing.html']
    jibing_keshi_name = ['呼吸内科', '消化内科', '泌尿内科', '心内科', '血液科', '内分泌科', '神经内科', '肾内科', '遗传病科', '风湿免疫科', '感染科',
                         '普外科', '骨外科', '神经外科', '心胸外科', '肝胆外科', '泌尿外科', '烧伤科', '肛肠科', '整形美容科', '妇科', '产科', '传染科',
                         '生殖健康', '男科', '皮肤科', '性病科', '中医科', '眼科', '口腔科', '耳鼻喉科',
                         '精神科', '心理科', '儿科综合', '小儿外科', '小儿内科', '营养科', '肿瘤内科', '肿瘤外科', '减肥', '康复科', '其他综合', '急诊科',
                         '肝病']
    # 症状按部位分类需要的url和name
    zhengzhuang_keshi_url = ['http://zzk.xywy.com/p/huxineike.html', 'http://zzk.xywy.com/p/xiaohuaneike.html',
                             'http://zzk.xywy.com/p/miniaoneike.html', 'http://zzk.xywy.com/p/xinneike.html',
                             'http://zzk.xywy.com/p/xueyeke.html', 'http://zzk.xywy.com/p/neifenmike.html',
                             'http://zzk.xywy.com/p/shenjingneike.html', 'http://zzk.xywy.com/p/shenneike.html',
                             'http://zzk.xywy.com/p/yichuanbingke.html', 'http://zzk.xywy.com/p/fengshimianyike.html',
                             'http://zzk.xywy.com/p/ganranke.html', 'http://zzk.xywy.com/p/puwaike.html',
                             'http://zzk.xywy.com/p/guwaike.html', 'http://zzk.xywy.com/p/shenjingwaike.html',
                             'http://zzk.xywy.com/p/xinxiongwaike.html', 'http://zzk.xywy.com/p/gandanwaike.html',
                             'http://zzk.xywy.com/p/miniaowaike.html', 'http://zzk.xywy.com/p/shaoshangke.html',
                             'http://zzk.xywy.com/p/gangchangke.html', 'http://zzk.xywy.com/p/zhengxingmeirongke.html',
                             'http://zzk.xywy.com/p/fuke.html', 'http://zzk.xywy.com/p/chanke.html',
                             'http://zzk.xywy.com/p/chuanranke.html', 'http://zzk.xywy.com/p/buyunbuyu.html',
                             'http://zzk.xywy.com/p/nanke.html', 'http://zzk.xywy.com/p/pifuke.html',
                             'http://zzk.xywy.com/p/xingbingke.html', 'http://zzk.xywy.com/p/zhongyizonghe.html',
                             'http://zzk.xywy.com/p/zhongyigushangke.html',
                             'http://zzk.xywy.com/p/zhongyililiaoke.html',
                             'http://zzk.xywy.com/p/zhongxiyijieheke.html', 'http://zzk.xywy.com/p/yanke.html',
                             'http://zzk.xywy.com/p/kouqiangke.html', 'http://zzk.xywy.com/p/erbihouke.html',
                             'http://zzk.xywy.com/p/jingshenke.html', 'http://zzk.xywy.com/p/xinlike.html',
                             'http://zzk.xywy.com/p/erkezonghe.html', 'http://zzk.xywy.com/p/xiaoerwaike.html',
                             'http://zzk.xywy.com/p/xiaoerneike.html', 'http://zzk.xywy.com/p/yingyangke.html',
                             'http://zzk.xywy.com/p/zhongliuneike.html', 'http://zzk.xywy.com/p/zhongliuwaike.html',
                             'http://zzk.xywy.com/p/yaopinke.html', 'http://zzk.xywy.com/p/zhongzhengjianhu.html',
                             'http://zzk.xywy.com/p/fuzhujiancha.html', 'http://zzk.xywy.com/p/kangfuke.html',
                             'http://zzk.xywy.com/p/liliaoke.html', 'http://zzk.xywy.com/p/qitazonghe.html',
                             'http://zzk.xywy.com/p/baojianyangsheng.html', 'http://zzk.xywy.com/p/jizhenke.html',
                             'http://zzk.xywy.com/p/tijianke.html']
    zhengzhuang_keshi_name = ['呼吸内科', '消化内科', '泌尿内科', '心内科', '血液科', '内分泌科', '神经内科', '肾内科', '遗传病科', '风湿免疫科', '感染科',
                              '普外科', '骨外科', '神经外科', '心胸外科', '肝胆外科', '泌尿外科', '烧伤科', '肛肠科', '整形美容科', '妇科', '产科', '传染科',
                              '生殖健康', '男科', '皮肤科', '性病科', '中医综合', '中医骨伤科', '中医理疗科', '中西医结合科', '眼科', '口腔科', '耳鼻喉科',
                              '精神科', '心理科', '儿科综合', '小儿外科', '小儿内科', '营养科', '肿瘤内科', '肿瘤外科', '药品科', '重症监护', '辅助检查', '康复科',
                              '理疗科', '其他综合', '保健养生', '急诊科', '体检科']

    spider = spider()
    # spider.get_body_part_jibing(jibing_buwei_url, jibing_buwei_name)
    # spider.get_body_part_zhengzhuang(zhengzhuang_buwei_url, zhengzhuang_buwei_name)
    # spider.get_character_jibing(jibing_character_url, jibing_character_name)
    spider.get_character_zhengzhuang(zhengzhuang_character_url, zhengzhuang_character_name)
    # spider.get_keshi_jibing(jibing_keshi_url, jibing_keshi_name)
    # spider.get_keshi_zhengzhuang(zhengzhuang_keshi_url, zhengzhuang_keshi_name)



