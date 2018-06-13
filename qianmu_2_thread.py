import threading
from queue import Queue
import requests
import lxml.etree
import time

START_URL = 'http://www.qianmu.org/2018USNEWS世界大学排名'
link_queue = Queue()
threads = []
DOWNLOADER_NUM = 10  # 定义线程数
downloader_pages = 0


def fetch(url, raise_err=False):
    global downloader_pages
    # print(url)
    try:
        r = requests.get(url)
    except Exception as e:
        print(e)
    else:
        downloader_pages += 1
        # 如果返回的状态码不是200,则报错
        if raise_err:
            r.raise_for_status()
    return r.text.replace('\t', '')


def parse(html):
    global link_queue
    selector = lxml.etree.HTML(html)
    links = selector.xpath('//*[@id="content"]/table/tbody/tr/td[2]/a/@href')
    for link in links:
        if not link.startswith('http://'):
            link = 'http://www.qianmu.org/%s' % link
        link_queue.put(link)  # 把页面的链接放到link_queue里面


def parse_university(html):
    selector = lxml.etree.HTML(html)
    table = selector.xpath('//*[@id="wikiContent"]/div[1]/table/tbody')
    if not table:
        return
    table = table[0]
    keys = table.xpath('./tr/td[1]//text()')
    cols = table.xpath('./tr/td[2]')
    values = [''.join(col.xpath('.//text()')) for col in cols]
    info = dict(zip(keys, values))
    print(info)


def downloader():
    while True:
        link = link_queue.get()
        if link is None:
            break
        parse_university(fetch(link))
        link_queue.task_done()
        print('remaining queue:%s' % link_queue.qsize())


if __name__ == '__main__':
    start_time = time.time()
    parse(fetch(START_URL, raise_err=True))
    # 创建线程对象
    for i in range(DOWNLOADER_NUM):
        t = threading.Thread(target=downloader)
        t.start()
        threads.append(t)  # 加入到线程池中
    link_queue.join()  # 让它堵塞

    for i in range(DOWNLOADER_NUM):
        link_queue.put(None)

    for t in threads:
        t.join()

    cost_seconds = time.time() - start_time
    print('download %s pages, cost %s seconds' % (downloader_pages, cost_seconds))
