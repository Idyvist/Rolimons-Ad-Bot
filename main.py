import requests, time, configparser, json, threading, ctypes, os
from threading import Thread

sent = 0
failed = 0
lock = threading.Lock()
os.system('cls')
headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
class Player:
    def __init__(self, config):
        self.userId = config['userId']
        self.roliVerification = config['roliVerification']
        self.roliData = config['roliData']
        Thread(target=self.overall).start()
        
    class Item:
        def __init__(self, id, value, uaid):
            self.id = id
            self.value = value
            self.uaid = uaid
        
    def get_inv(self):
        user_response = json.loads(
                requests.get("https://www.rolimons.com/api/playerassets/" + str(self.userId), headers=headers).text)
        items_response = json.loads(
                requests.get("https://www.rolimons.com/itemapi/itemdetails", headers=headers).text)
        asset_ids = list(user_response["playerAssets"].keys())
        assets = []
        
        for asset_id in asset_ids:
            item_value = int(items_response.get('items', {}).get(asset_id)[4])
            item_uaids = user_response['playerAssets'][asset_id]
            uaids_on_hold = user_response['holds']
            
            for uaid in item_uaids:
                if uaid not in uaids_on_hold:
                    item = self.Item(asset_id, item_value, item_uaids)
                    assets.append(item)

        assets.sort(key=lambda x: x.value, reverse=True)
        
        for asset in assets:
            assets[assets.index(asset)] = int(asset.id)
            
        return assets[:4]

        
    def send(self):
        global sent, failed
        offer_items = self.get_inv()
        r = requests.post(
            'https://www.rolimons.com/tradeapi/create',

            cookies = {
                '_RoliVerification': self.roliVerification,
                '_RoliData': self.roliData
                },

            json = {
                "player_id": self.userId,
                "offer_item_ids": offer_items,
                "request_item_ids": [],
                "request_tags":["any", "upgrade", "downgrade"]
                }
            )

        if r.json()['success'] == True:
            print("Trade ad created")
            sent += 1
        else:
            print("Failed to create trade ad")
            failed += 1


    def overall(self):
        while True:
            self.send()
            time.sleep(60 * 20)

def title():
    while True:
        ctypes.windll.kernel32.SetConsoleTitleW(f'Sent: {sent} | Failed: {failed}')
        time.sleep(1)

Thread(target=title).start()

for root, dirs, files in os.walk("."):
    for filename in files:
        if 'config' in filename:
            with open(f'{filename}','r') as config:
                config = json.load(config)
            c = Player(config)
