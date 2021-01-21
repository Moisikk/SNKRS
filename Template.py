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

logging.basicConfig(filename='log.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
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
    #URL SCRAPE SITE
    url = ''        
    #URL SCRAPE SITE                                                    
    s = requests.Session()
    html = s.get(url=url, headers=headers, verify=False, timeout=15)
    soup = BeautifulSoup(html.text, 'html.parser')
    itemsName = soup.find_all('p', {'class': 'manufacturer-name'})
    itemsModel = soup.find_all('h2', {'itemprop': 'name'})
    itemsRedirect = soup.find_all('h2', {'itemprop': 'name'})
    itemsImage = soup.find_all('img', {'class': 'hover-img'})
    itemsPrice = soup.find_all('span',{'class':'price'})
    ################## DE FACUT SA CAUTE MARIMI
    itemsSizes = soup.find_all('h2', {'class': 'h2'})
    ################## DE FACUT SA CAUTE MARIMI
    for i in range(48):
        itemsName[i] = itemsName[i].text
        itemsModel[i] = itemsModel[i].text
        itemsRedirect[i] = itemsRedirect[i].find('a')['href']
        itemsImage[i] = itemsImage[i]['data-full-size-image-url']
        itemsPrice[i] = itemsPrice[i].text
        itemsSizes[i] = itemsSizes[i].text
        
        print(f'Brand: {itemsName[i]}\nModel: {itemsModel[i]}\nLink: {itemsRedirect[i]}\nImagine: {itemsImage[i]}\nPret: {itemsPrice[i]}\nMarimi: {itemsSizes[i]}')
        item = [itemsName[i],itemsModel[i],itemsRedirect[i],itemsImage[i],itemsPrice[i],itemsSizes[i]]
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
    embed["title"] = f"{product_item[0]}{product_item[1]}"  # Nume produs
    embed["description"] = f"**Pret:**\n{product_item[4]}\n**Marimi**:\n{product_item[5]}" # Model produs
    embed['url'] = f'{product_item[2]}'  # Link produs
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

def checkItems(items):
    for i in range(0,48):
        if not items[i] in lastItems:
            time.sleep(0.5)
            discord_webhook(items[i])
    for i in range(0,48):
        lastItems[i] = items[i]


true = True

def monitor():
    while true==True:
        currentItems = scrape_main_site(headers)
        checkItems(currentItems)
        time.sleep(30)

monitor()