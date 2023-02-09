import os
from random import randint
import concurrent.futures

import requests
from PIL import Image
from lxml.html import fromstring


def pick_random_proxy(proxies):
    # pick random proxy to avoid captcha
    chosen_proxy = proxies[randint(0, len(proxies) - 1)].split('@')
    proxy = {"http": f"http://{chosen_proxy[1]}@{chosen_proxy[0]}",
             "https": f"http://{chosen_proxy[1]}@{chosen_proxy[0]}"}

    return proxy


def get_urls(link, proxies):

    # get html tree of a main page
    response = session.get(link, proxies=pick_random_proxy(proxies))
    html_tree = fromstring(response.content)

    # get number of items on the page (e.g. in my case there were 32 ("step") items on each and 132 ("max") total items)
    number = "".join(html_tree.xpath('//div[@class="results-hits"]/text()'))
    number = [int(s) for s in number.replace('\n', ' ').split() if s.isdigit()]
    step, maximum_items = number[1], number[2]

    # iterate over pages. here we send AJAX queries, where we specify number of first item on the page and step
    current_items = 0
    urls = []

    for i in range(int((maximum_items/step)+(maximum_items % step > 0))+1):

        # send AJAX query
        ajax_query = 'https://www.ralphlauren.nl/en/men/clothing/hoodies-sweatshirts/10204?sw1=sw-cache-me&webcat=' \
                   f'men%7Cclothing%7Cmen-clothing-hoodies-sweatshirts&start={current_items}&sz={step}&format=ajax'
        response = session.get(ajax_query, proxies=pick_random_proxy(proxies))

        # collect all urls to items
        html_tree = fromstring(response.content)
        urls = urls + html_tree.xpath('//a[@class="name-link"]/@href')
        current_items += step

    return urls


def scrape_images(url, proxies):

    # get HTML tree of a page with item
    link = 'https://ralphlauren.nl' + url
    response = session.get(link, proxies=pick_random_proxy(proxies))
    html_tree = fromstring(response.content)

    # check if page contains more than 2 pictures of item. This will filter out items without pictures with person
    # like this: https://goo.su/KPZf
    check_xpath = ''.join(html_tree.xpath('//img[@aria-label="Product Image 3"]/@src'))
    if len(check_xpath) < 5:
        html_tree = []

    # get picture's URLs and item's ID (to name pictures)
    picture_with_man = ''.join(html_tree.xpath('(//picture[@class="swiper-zoomable"])[1]/@data-highres-images'))
    picture_without_man = ''.join(html_tree.xpath('(//picture[@class="swiper-zoomable"])[2]/@data-highres-images'))
    item_number = ''.join(html_tree.xpath('//div[@class="product-number"]/span/text()'))

    # download pictures into separate folders
    img = Image.open(requests.get(picture_with_man, stream=True).raw)
    img.save(f'download/with_person/{item_number}_with_person.jpeg')
    img = Image.open(requests.get(picture_without_man, stream=True).raw)
    img.save(f'download/without_person/{item_number}_without_person.jpeg')


if __name__ == "__main__":

    # read proxies from file. site doesn't work in Russia and bans scraper by IP, so we need to rotate them
    with open("proxies.txt", "r") as file:
        proxies = file.read().split("\n")

    # session and user-agent for requests
    session = requests.Session()
    session.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/110.0.0.0 Safari/537.36',
        'origin': 'https://www.ralphlauren.nl',
        'referer': 'https://www.ralphlauren.nl/'
    }

    # create folders to store images
    for folder in ['download', 'download/with_person', 'download/without_person']:
        if not os.path.exists(folder):
            os.mkdir(folder)

    # get URLs list
    link = "https://www.ralphlauren.nl/en/men/clothing/hoodies-sweatshirts/10204?webcat=men%" \
           "7Cclothing%7Cmen-clothing-hoodies-sweatshirts"
    urls = get_urls(link, proxies)

    # download pictures
    not_downloaded = []
    for url in urls:
        try:
            scrape_images(url, proxies)
        except Exception:
            not_downloaded = not_downloaded + [url]
            continue

    print(f'{len(urls)-len(not_downloaded)} pictures downloaded.')
    print(f'Troublesome URLS: {not_downloaded}')


# multiprocessing part. This approach got my precious proxies banned by Ralph Lauren site, so it's unused
"""
# launch image downloading with multithreading
if len(urls) > 0:
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, (len(urls) + 1))) as executor:
        gen = executor.map(scrape_images, urls)
"""
