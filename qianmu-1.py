import requests
import lxml.etree

START_URL = 'http://www.qianmu.org/2018USNEWS世界大学排名'
link_queue = [] # 定义全局的队列
# 取得url
def fetch(url):
    r =requests.get(url)
    return r.text.replace('\t','')
# 解析html
def parse(html):
    global link_queue
    selector = lxml.etree.HTML(html)
    links = selector.xpath('//*[@id="content"]/table/tbody/tr/td[2]/a/@href')
    # print(links)
    link_queue += links

def parse_university(html):
    selector = lxml.etree.HTML(html)
    table = selector.xpath('//*[@id="wikiContent"]/div[1]/table/tbody')
    if not table:
        return
    table = table[0]
    keys = table.xpath('./tr/td[1]//text()')
    cols = table.xpath('./tr/td[2]')
    values = [''.join(col.xpath('.//text()')) for col in cols]
    info = dict(zip(keys,values))
    print(info)

if __name__ == '__main__':
    parse(fetch(START_URL))
    print(link_queue)
    for link in link_queue:
        if not link.startswith('http://'):
            link = 'http://www.qianmu.org/%s'%link
        parse_university(fetch(link))






