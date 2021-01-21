import requests
from bs4 import BeautifulSoup
import logging
import dotenv
import datetime
import json
import time
import urllib3
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, HardwareType

logging.basicConfig(filename='Zalandolog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

INSTOCK = []

"""
TO DO: EMBED MESSAGE DISCORD .
"""

def scrape_main_site(headers, proxy):
    """
    Scrape the Sneaker Industry site and adds each item to an array
    :return:
    """
    items = []
    url = 'https://sneakerindustry.ro/ro/produse-noi'
    s = requests.Session()
    html = s.get(url=url, headers=headers, proxies=proxy, verify=False, timeout=15)
    soup = BeautifulSoup(html.text, 'html.parser')
    itemsName = soup.find_all('p', {'class': 'manufacturer-name'})
    itemsModel = soup.find_all('h2', {'itemprop': 'name'})
    itemsRedirect = soup.find_all('h2', {'itemprop': 'name'})
    itemsImage = soup.find_all('img', {'class': 'hover-img'})
    for i in range(48):
        itemsName[i] = itemsName[i].text
        itemsModel[i] = itemsModel[i].text
        itemsRedirect[i] = itemsRedirect[i].find('a')['href']
        itemsImage[i] = itemsImage[i]['data-full-size-image-url']
        print(f'Brand: {itemsName[i]}\nModel: {itemsModel[i]}\nLink: {itemsRedirect[i]}\nImagine: {itemsImage[i]}')
        item = [itemsName[i],itemsModel[i],itemsRedirect[i],itemsImage[i]]
        items.append(item)
    return items
    

def discord_webhook(product_item):
    """
    Sends a Discord webhook notification to the specified webhook URL
    :param product_item: An array of the product's details
    :return: None
    """
    data = {}
    data["username"] = CONFIG['USERNAME']
    data["avatar_url"] = CONFIG['AVATAR_URL']
    data["embeds"] = []
    embed = {}
    if product_item == 'initial':
        embed["description"] = "Multumim ca folosesti discord-ul Busta Romania!"
    else:
        embed["title"] = product_item[0]  # Nume produs
        embed["description"] = product_item[1]
        embed["thumbnail"] = {'url': product_item[3]}  # Imagine produs

    embed["color"] = int(CONFIG['COLOUR'])
    embed["footer"] = {'text': 'Powered by Busta Romania.'}
    embed["timestamp"] = str(datetime.datetime.utcnow())
    data["embeds"].append(embed)

    result = requests.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info("Payload delivered successfully, code {}.".format(result.status_code))


def checker(item):
    """
    Determines whether the product status has changed
    :param item: list of item details
    :return: Boolean whether the status has changed or not
    """
    for product in INSTOCK:
        if product == item:
            return True
    return False


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    :param mylist: list
    :return: list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(item, start):
    if not checker(item):
        INSTOCK.append(item)
        if start == 0:
            discord_webhook(item)


def monitor():
    """
    Initiates monitor
    :return:
    """
    print('PORNim monitorizarea.')
    logging.info(msg='Monitorizarea a inceput.')
    discord_webhook('initial')
    start = 1
    proxy_no = 0

    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            items = remove_duplicates(scrape_main_site(headers, proxy))
            for item in items:
                check = False
                if keywords == '':
                    comparitor(item, start)
                else:
                    for key in keywords:
                        if key.lower() in item[0].lower():
                            check = True
                            break
                    if check:
                        comparitor(item, start)
            time.sleep(float(CONFIG['DELAY']))
            start = 0
        except Exception as e:
            print(e)
            logging.error(e)
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
            if proxy != {}:
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
