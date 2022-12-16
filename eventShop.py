# 通行證代幣兌換

import requests, json
import re
import base64

from auth import *

requests.packages.urllib3.disable_warnings()

def printJSON(data):
	if isinstance(data, str) or isinstance(data, int): print(data)
	else: print(json.dumps(data, ensure_ascii=False, indent=4))

class eventShop():
	def __init__(self, auth):
		self.auth = auth
		self.baseAuth = f"Basic {self.getBasicAuth(auth)}"
		self.header = {
			'User-Agent': "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/12.23.483.5208 (CEF 91) Safari/537.366",
			'Content-Type': 'application/json',
			'Authorization': self.baseAuth,
		}
		self.evtData = self.getEventHeaderData()
		self.balance = self.getBalance()

	def getBasicAuth(self, auth):
		reAuth = re.search(r'https://(riot:.+?)@127\.0\.0\.1:(\d+?)', auth).group(1)
		baseAuth = base64.b64encode(reAuth.encode('UTF-8')).decode('UTF-8')
		return baseAuth
	def getEventHeaderData(self):
		url = f"{self.auth}/lol-event-shop/v1/event-header-data"
		return requests.get(url, verify=False, headers=self.header).json()
	def getBalance(self):
		url = f"{self.auth}/lol-event-shop/v1/lazy-load-data"
		res = requests.post(url, verify=False, headers=self.header)
		url = f"{self.auth}/lol-event-shop/v1/token-balance"
		res = requests.get(url, verify=False, headers=self.header)
		return int(res.text)
	def getOffer(self, target='隨機英雄碎片'):
		url = f"{self.auth}/lol-event-shop/v1/categories-offers"
		res = requests.get(url, verify=False, headers=self.header).json()
		for category in res:
			if category['category'] != 'Loot':
				continue
			for offer in category['offers']:
				if target in offer['localizedTitle']: # target
					return offer
		return False
	def purchaseOffer(self, target='隨機英雄碎片', maxToken=300):
		offer = self.getOffer(target=target)
		if not offer or self.balance >= maxToken:
			return False
		count = int(self.balance / offer['price'])
		for i in range(count):
			url = f"{self.auth}/lol-event-shop/v1/purchase-offer"
			data = {'offerId': offer['id']}
			res = requests.post(url, verify=False, headers=self.header, json=data)
			if res.status_code != 200:
				count -= 1
		if count:
			return {'cost': int(count*offer['price']), 'count': count, 'tokenName':f"{self.evtData['eventName']}代幣", 'target':offer['localizedTitle']}
		else:
			return False
def getParser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", "--folder", default="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
	parser.add_argument("-t", "--token",  default="")
	return parser

if __name__ == '__main__':
	import argparse
	parser = getParser()
	args = parser.parse_args()

	auth = getAuth2()
	auth = getAuth(args.dir) if not auth else auth

	evt = eventShop(auth)
	print(evt.purchaseOffer(target='隨機英雄碎片', maxToken=300))