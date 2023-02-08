#!/usr/bin/python
"""
Скрипт для парсинга поисковой выдачи Google (1-й страницы)
может работать через vpn, tor.
Записывает html код страницы выдачи Google и json файл содержащий ссылки, заголовки и описания.
"""
import json
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait


def init_driver(
        show: bool = False,
        proxy: bool = False,
        proxy_type: str = '',
        proxy_http: str = '',
        proxy_port: int = 0,
        proxy_pac: str = ''):
    """
    Initial web driver (firefox),
    :param: show: show firefox webdriver window
    :param: proxy: enable proxy
    :param: proxy_type: enter proxy type, valid values:
                'tor'—for connect to tor proxy, 
                'proxy'—for connect to proxy,
                'proxy_pac'—for connect by proxy.pac file or net address of proxy.pac file
    :param: proxy_http: enter ip of http proxy
    :param: proxy_port: enter port http proxy
    :param: proxy_pac: enter a path of proxy.pac file
    :return: driver: selenium.webdriver.Firefox with settings.
    """
    options = webdriver.FirefoxOptions()
    if not show:
        options.arguments.append("-headless")  # disable visibility of window
    if proxy:
        if proxy_type == "tor":
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.socks", proxy_http)
            options.set_preference("network.proxy.socks_port", proxy_port)
            options.set_preference("network.proxy.socks_remote_dns", False)
        elif proxy_type == "proxy":
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", proxy_http)
            options.set_preference("network.proxy.http_port", proxy_port)
            options.set_preference("network.proxy.ssl", proxy_http)
            options.set_preference("network.proxy.ssl_port", proxy_port)
        elif proxy_type == "proxy_pac":
            options.set_preference("network.proxy.type", 2)
            options.set_preference("network.proxy.autoconfig_url", proxy_pac)
    # set firefox options
    driver = webdriver.Firefox(options=options)
    # set wait of page load
    driver.wait = WebDriverWait(driver, 5)
    return driver


def get_page_by_searched_text(driver, search: str):
    """
    Get google page with results of inputted text and print result into a source.html file
    :param driver: firefox webdriver
    :param search: text line for enter in input element.
    """
    driver.get('https://www.google.com')
    # uncomment 2 lines above if Google show page with setting up settings
    # send = driver.find_elements(by='tag name', value='button')
    # send[2].click()
    # find input element
    input_element = driver.find_element(by='tag name', value='input')
    # type to input element inputted text
    input_element.send_keys(search)
    # type enter
    input_element.send_keys(Keys.RETURN)

    # waiting for a page loaded
    time.sleep(10)

    # print result into source.html file
    with open('source.html', 'w', encoding='utf-8') as file:
        file.write(driver.page_source)


def parse_page() -> list[dict]:
    """
    Parse HTML file with bs4
    :return: links: dict with a link, small text and text description.
    """
    # read source.html.
    with open('source.html', 'r', encoding='utf-8') as file:
        source = file.read()
    soup = BeautifulSoup(source, 'lxml')
    # get div with the id=search
    search = soup.find('div', id='search')
    # find all sites searched in google
    elements = search.find_all('div', class_='kvH3mc BToiNc UK95Uc')
    links = []
    # get links, small text and description in elements
    for element in elements:
        link = element.find('a').get('href')
        text = element.find('a').find('h3').text
        description = element.find('div', class_='Z26q7c UK95Uc').text
        links.append({'link': link, 'text': text, 'description': description})
    return links


def main(search: str,
         show: bool = False,
         proxy: bool = False,
         proxy_type: str = '',
         proxy_http: str = '',
         proxy_port: int = 80,
         proxy_pac: str = ''):
    """
    Call all functions for get links from Google searched page.
    :param show: Show firefox webdriver window
    :param proxy: enable proxy
    :param proxy_type: enter proxy type, valid values:
                'tor'—for connect to tor proxy, 
                'proxy'—for connect to proxy,
                'proxy_pac'—for connect by proxy.pac file or net address of proxy.pac file
    :param proxy_http: enter ip of http proxy
    :param proxy_port: enter port http proxy
    :param proxy_pac: enter a path of proxy.pac file
    :param search: String for enter Google.
    """
    driver = init_driver(
        show=show,
        proxy=proxy,
        proxy_type=proxy_type,
        proxy_http=proxy_http,
        proxy_port=proxy_port,
        proxy_pac=proxy_pac)

    get_page_by_searched_text(driver, search)
    links = parse_page()
    # print links to json file
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(links, file, indent=4, ensure_ascii=False)

    # close webdriver
    driver.quit()
    # remove log file from geckodriver(firefox).
    os.remove("geckodriver.log")


if __name__ == "__main__":
    main("python projects", show=True, proxy=True, proxy_type="tor",
         proxy_http='127.0.0.1', proxy_port=9050)
    # main('python projects', show=True, proxy=True, proxy_type='proxy_pac',
    #      proxy_pac='https://antizapret.prostovpn.org/proxy.pac')
    # main('python projects', show=True, proxy=True, proxy_type='proxy',
    #      proxy_http='127.0.0.1', proxy_port=80)
