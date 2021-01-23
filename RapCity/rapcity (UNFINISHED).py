import requests
from bs4 import BeautifulSoup
import logging
import dotenv
import datetime
import json
import time
import re
import urllib3
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, HardwareType

logging.basicConfig(filename='RapCitylog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()
headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}

def scrape_main_site(headers):
    """
    Scrape the Sneaker Industry site and adds each item to an array
    :return:
    """
    items = []
    url = 'https://www.rapcity.ro/ujdonsagok?ccsop=CIP'
    s = requests.Session()
    html = s.get(url=url, headers=headers, verify=False, timeout=15)
    soup = BeautifulSoup(html.text, 'html.parser')
    itemsName = soup.find_all('h2',{'class':'cl-item-title'})
    itemsColor = soup.find_all('div',{'class':'cl-item-color'})
    itemsRedirect = soup.find_all('a',{'class':'cl-item col-xs-6 col-sm-4 col-md-3'})
    itemsImage = soup.find_all('div',{'class':'cl-item-overlay'})
    itemsPrice = soup.find_all('span',{'class':'price-normal'})
    print(itemsImage)
    for i in range(12):
        itemsName[i]=itemsName[i].text
        itemsRedirect[i]=itemsRedirect[i]['href']
        itemsImage[i]=itemsImage[i].find('img')
        print(itemsImage[i])
        itemsImage[i]=itemsImage[i]['src']
        itemsImage[i]=f'https://www.rapcity.ro{itemsImage[i]}'
        itemsPrice[i]=itemsPrice[i].text
        itemsColor[i]=itemsColor[i].text
        print(f'Brand: {itemsName[i]}\nLink: {itemsRedirect[i]}\nImagine: {itemsImage[i]}\nPret: {itemsPrice[i]}\nCuloare: {itemsColor[i]}')
        item = [itemsName[i],itemsRedirect[i],itemsImage[i],itemsPrice[i],itemsColor[i]]
        items.append(item)
    return items

lastItems = scrape_main_site(headers)

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
    embed["title"] = f"{product_item[0]}"  # Nume produs
    embed["description"] = f"**Pret:**\n{product_item[3]}\n**Culoare:**{product_item[4]}" # Model produs
    embed['url'] = f'{product_item[1]}'  # Link produs
    embed["thumbnail"] = {'url': product_item[2]}  # Imagine produs
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
        print("Mesaj trimis cu succes, code {}.".format(result.status_code))
        logging.info("Mesaj trimis cu succes, code {}.".format(result.status_code))

def checkItems(items):
    for i in range(0,12):
        if not items[i] in lastItems:
            time.sleep(0.5)
            discord_webhook(items[i])
    for i in range(0,12):
        lastItems[i] = items[i]


true = True

def monitor():
    while true==True:
        currentItems = scrape_main_site(headers)
        checkItems(currentItems)
        time.sleep(30)

monitor()

######################################################################################################
###############    DACA CITESTI ASTA, SA MOARA MAMA CA M-AM CHINUIT ZILE COAIE    ####################
######################################################################################################