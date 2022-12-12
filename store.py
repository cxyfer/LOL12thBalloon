import requests, json
import re
import base64

storeUrl = "https://tw.store.leagueoflegends.com/"
UA = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/12.14.456.5556 (CEF 91) Safari/537.36"

def purchaseItem(idToken, acId, iType, itemIds, ipCost, rpCost=None, quantity=1): #沒辦法判斷是否購買成功
	url = storeUrl + "storefront/v3/purchase?language=zh_TW"
	header = {"User-Agent": UA, "Referer": storeUrl, "AUTHORIZATION": f"Bearer {idToken}", "Content-Type": "application/json"}
	if isinstance(itemIds, list): # 20220805後只能分批購買
		items = [{"inventoryType":iType, "itemId":itemId, "ipCost":ipCost, "rpCost":rpCost, "quantity":quantity} for itemId in itemIds]
	else:
		items = [{"inventoryType":iType, "itemId":itemIds, "ipCost":ipCost, "rpCost":rpCost, "quantity":quantity}]
	data = {"accountId":acId, "items": items}
	res = requests.post(url, verify=False, headers=header, json=data).json()
	if "order" in res:
		if res['order']['status']['status'] == "ACCEPTED":
			trans = [ f"{tran['inventoryType']}_{tran['itemId']}" for tran in res['transactions'] ]
			#print(f"  購買 {','.join(trans)} 成功，剩餘 IP:{res['ipBalance']} RP:{res['rpBalance']}")
			return True
	return False
	

def buy1Icons(idToken, acId):
	#purchaseItem(idToken, acId, "BUNDLES", 99901185, ipCost=1)
	#purchaseItem(idToken, acId, "SUMMONER_ICON", [1448,1449,1594] , ipCost=1)
	purchaseItem(idToken, acId, "SUMMONER_ICON", 1448 , ipCost=1)
	purchaseItem(idToken, acId, "SUMMONER_ICON", 1449 , ipCost=1)
	purchaseItem(idToken, acId, "SUMMONER_ICON", 1594 , ipCost=1)
	purchaseItem(idToken, acId, "SUMMONER_ICON", 3218 , ipCost=1) # 普羅點心時間
	purchaseItem(idToken, acId, "EMOTE", 4033 , ipCost=1) # 好了，拿去吧


def purchaseNameChange(idToken, acId, name, useRP=False): #不能突破字數限制
	url = storeUrl + "storefront/v3/summonerNameChange/purchase?language=zh_TW"
	header = {"User-Agent": UA, "Referer": storeUrl, "AUTHORIZATION": f"Bearer {idToken}", "Content-Type": "application/json"}
	items = [{"inventoryType":"SUMMONER_CUSTOMIZATION", "itemId":1, "ipCost":13900, "rpCost":None, "quantity":1}]
	data = {"summonerName":name, "accountId":acId, "items":items}
	res = requests.post(url, verify=False, headers=header, json=data).json()
	if 'summonerName' in res:
		print(f"  改名 {res['summonerName']} 成功，請重啟遊戲客戶端")
	elif 'message' in res:
		print(res['message'])
	else:
		print(json.dumps(res, ensure_ascii=False, indent=4))
	return True if 'summonerName' in res else False

def newNameChange(auth, name="這是一個召喚師名稱測試專用帳號"):
	url = auth + "/lol-summoner/v1/summoners"
	auth2 = re.search(r'https://(riot:.+?)@127\.0\.0\.1:(\d+?)', auth).group(1)
	token = base64.b64encode(auth2.encode('UTF-8')).decode('UTF-8')
	header = {"Authorization": f"Basic {token}", "Content-Type": "application/json", "User-Agent":UA}
	data = {"name": name}
	res = requests.post(url, verify=False, headers=header, json=data).json()
	if 'displayName' in res:
		print(f"  新帳號創立成功：{res['displayName']}")
	else:
		print(json.dumps(res, ensure_ascii=False, indent=4))
def oldNameChange(auth, name="這是一個召喚師名稱測試專用帳號"):
	url = auth + "/lol-summoner/v1/current-summoner/name"
	auth2 = re.search(r'https://(riot:.+?)@127\.0\.0\.1:(\d+?)', auth).group(1)
	token = base64.b64encode(auth2.encode('UTF-8')).decode('UTF-8')
	header = {"Authorization": f"Basic {token}", "Content-Type": "application/json", "User-Agent":UA}
	data = f'\"{name}\"'.encode() # 要加雙引號= =
	res = requests.post(url, verify=False, headers=header, data=data)
	res = res.json()
	if 'displayName' in res:
		print(f"  舊帳號改名成功：{res['displayName']}")
	else:
		print(json.dumps(res, ensure_ascii=False, indent=4))

if __name__ == '__main__':
	print()