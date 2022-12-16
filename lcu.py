import os, re, time, datetime
import requests, json
import argparse
import sql

from lol_chat import *
from auth import *
import store
from eventShop import eventShop

requests.packages.urllib3.disable_warnings()
def printLog(text1, end="\n"):
	print(text1, end=end)
	with open("lcu.log","a", encoding = 'utf8') as data:
		timeinfo = time.strftime("%Y%m%d", time.localtime()) 
		data.write(f"{timeinfo} | {str(text1).strip()}{end}")
def printJSON(data):
	if isinstance(data, str) or isinstance(data, int): print(data)
	else: print(json.dumps(data, ensure_ascii=False, indent=4))
def getSummoner(auth):
	url = auth + "/lol-summoner/v1/current-summoner" #url = auth + "/lol-login/v1/session"
	res = requests.get(url, verify=False)
	rj = json.loads(res.text)
	return {"summonerId": rj["summonerId"], "accountId": rj["accountId"], "puuid": rj["puuid"], "name":rj["displayName"] , "level":rj["summonerLevel"]}
def getSession(auth):
	url = auth + "/lol-login/v1/session"
	res = requests.get(url, verify=False).json()
	return res
	
#​/lol-champions​/v1​/inventories​/{summonerId}​/champions-playable-count
def getChampion(auth):
	url = auth + "/lol-champions/v1/owned-champions-minimal"
	res = requests.get(url,verify=False).json()
	champs, champsId, champList, champListEN = [], [], [], []
	for champ in res:
		if champ["ownership"]["owned"]:
			champs.append(champ["name"])
			champsId.append(champ["id"])
			if champ["id"] not in [1,5,10,11,13,15,16,18,19,20,22,27,32,36,37,51,53,54,57,78,81,86,90,99,102]:
				champList.append(champ["name"])
				champListEN.append(champ["alias"])
	return {"all":champs, "allId":champsId, "simple":champList, "simpEN":champListEN}
def getSkin(auth, summonerId):
	url = auth + f"/lol-champions/v1/inventories/{summonerId}/skins-minimal"
	res = requests.get(url,verify=False).json()
	skinList = []
	for skin in res:
		if skin["ownership"]["owned"] and not skin["ownership"]["rental"]['endDate'] and not str(skin["id"]).endswith("000"):
			skinList.append(skin["name"])
	return skinList
def getWallet(auth):
	url = auth + "/lol-store/v1/wallet"
	res = requests.get(url,verify=False).json()
	return res
def getLootMap(auth, repeat=0):
	url = auth + "/lol-loot/v1/refresh"
	res = requests.post(url , verify=False, json={"force":True})
	url = auth + "/lol-loot/v1/player-loot-map"
	res = requests.get(url,verify=False).json()
	return res if not repeat else getLootMap(auth, repeat-1)
def getLoot(auth, ownChamps=[], upgradeBelow=0, disenchantBelow=0, useCurrencyMythic=False, useCoin=False, useCoinCURRENCY=False):
	rJ = getLootMap(auth, repeat=3)

	if "MATERIAL_key_fragment" in rJ.keys() and rJ['MATERIAL_key_fragment']['count']>=3: #合成鑰匙
		getHexCraft(auth, ["MATERIAL_key_fragment"], "MATERIAL_key_fragment_forge", repeat=rJ['MATERIAL_key_fragment']['count']//3) #合成鑰匙
		rJ = getLootMap(auth)
	while ("MATERIAL_key" in rJ.keys() and "CHEST_224" in rJ.keys()): #精雕寶箱
		getHexCraft(auth, ["CHEST_224","MATERIAL_key"], "CHEST_224_OPEN", repeat=min(rJ['MATERIAL_key']['count'], rJ['CHEST_224']['count']))
		rJ = getLootMap(auth)
	while ("MATERIAL_key" in rJ.keys() and "CHEST_generic" in rJ.keys()): #一般寶箱
		getHexCraft(auth, ["CHEST_generic","MATERIAL_key"] , "CHEST_generic_OPEN", repeat=min(rJ['MATERIAL_key']['count'], rJ['CHEST_generic']['count'])) 
		rJ = getLootMap(auth)
	while ("MATERIAL_key" in rJ.keys() and "CHEST_champion_mastery" in rJ.keys()): #英雄寶箱
		getHexCraft(auth, ["CHEST_champion_mastery","MATERIAL_key"] , "CHEST_champion_mastery_OPEN", repeat=min(rJ['MATERIAL_key']['count'], rJ['CHEST_champion_mastery']['count'])) 
		rJ = getLootMap(auth)
 
	# 代幣兌換
	MTRL = "MATERIAL_"
	for item in rJ.keys():
		reMTRL = re.match(r'MATERIAL_\d{3,4}', item)
		if reMTRL: 
			MTRL = reMTRL.group(0)

	if MTRL in rJ.keys() and useCoin: 
		for recipe in getRecipes(auth, MTRL):
			if recipe['description'] == "1 隨機英雄碎片": recipe_CHEST_241 = recipe['recipeName']
			if recipe['description'] == "10 藍色結晶粉末": recipe_CURRENCY = recipe['recipeName']
		if rJ[MTRL]['count']>=50 and rJ[MTRL]['count']<useCoin: #世界大賽代幣兌換神秘英雄
			getHexCraft(auth, [MTRL], recipe_CHEST_241, repeat=rJ[MTRL]['count']//50)
			rJ = getLootMap(auth)
		if MTRL in rJ.keys() and useCoinCURRENCY: 
			if rJ[MTRL]['count'] < useCoinCURRENCY:
				getHexCraft(auth, [MTRL], recipe_CURRENCY, repeat=rJ[MTRL]['count'])
				rJ = getLootMap(auth)
	'''chestList = ["CHEST_425"] #晶球
	for i in range(480, 580): chestList.append("CHEST_{}".format(i)) #禮包
	for i in range(128, 160): chestList.append("CHEST_{}".format(i)) #升等
	for i in range(290, 300): chestList.append("CHEST_{}".format(i)) #里程碑
	chestList += ["CHEST_185","CHEST_186", "CHEST_199"] #升等
	chestList += ["CHEST_3330078", "CHEST_3330107", "CHEST_3330110"] #精靈蛋
	chestList += ["CHEST_241"] #神秘英雄碎片(代幣)
	chestList += ["CHEST_187"] #神秘表情
	chestList += ["CHEST_206"] #榮譽等級典藏罐
	chestList += ["CHEST_6670001"] #永恆精雕 第 1 系列 典藏罐
	for chest in chestList:
		if chest in rJ.keys():
			getHexCraft(auth, [chest], "{}_OPEN".format(chest), repeat=rJ[chest]['count'])
			rJ = getLootMap(auth)'''
	openChest = False
	for item in rJ.keys():
		reChest = re.match(r'CHEST_\d+', item) # 開啟所有寶箱
		if reChest and item not in ["CHEST_224", "CHEST_generic", "CHEST_champion_mastery"]: 
			getHexCraft(auth, [item], "{}_OPEN".format(item), repeat=rJ[item]['count'])
			rJ = getLootMap(auth)
			openChest = True
		if item.startswith("STATSTONE_SHARD"): # 分解永恆精雕
			getHexCraft(auth, [item], "STATSTONE_SHARD_DISENCHANT", repeat=rJ[item]['count'])
		elif item.startswith("STATSTONE"): # 分解永恆精雕
			getHexCraft(auth, [item], "STATSTONE_DISENCHANT", repeat=rJ[item]['count'])
	rJ = getLootMap(auth)
	if openChest:
		return getLoot(auth, ownChamps, upgradeBelow, disenchantBelow, useCurrencyMythic, useCoin, useCoinCURRENCY)

	# CURRENCY_mythic
	if "CURRENCY_mythic" in rJ.keys() and useCurrencyMythic: #神話結晶粉末 兌換 
		if rJ['CURRENCY_mythic']['count'] <= useCurrencyMythic:
			getHexCraft(auth, ["CURRENCY_mythic"], "CURRENCY_mythic_forge_16", repeat=rJ['CURRENCY_mythic']['count']) #神話結晶粉末 兌換 150藍粉
			#getHexCraft(auth, ["CURRENCY_mythic"], "CURRENCY_mythic_forge_15", repeat=rJ['CURRENCY_mythic']['count']) #神話結晶粉末 兌換 35 橘粉
			rJ = getLootMap(auth)

	count_be, count_OE = 0, 0
	skinList = [loot["itemDesc"] for key, loot in rJ.items() if loot["displayCategories"] == "SKIN"] #備用
	champList = [loot["itemDesc"] for key, loot in rJ.items() if loot["displayCategories"] == "CHAMPION"] #備用

	own_OE = rJ['CURRENCY_cosmetic']['count'] if 'CURRENCY_cosmetic' in rJ else 0
	for key, loot in rJ.items():
		if loot["displayCategories"] == "CHAMPION":
			count_be += loot["disenchantValue"] * loot["count"]
			if loot["count"] > 1 or loot["storeItemId"] in ownChamps or loot["value"] <= disenchantBelow: #分解重複和已擁有的英雄碎片
				if loot["lootName"].startswith("CHAMPION_RENTAL"):
					getHexCraft(auth, [loot["lootName"]], "CHAMPION_RENTAL_disenchant")
				else:
					getHexCraft(auth, [loot["lootName"]], "CHAMPION_disenchant")
				return getLoot(auth, ownChamps, upgradeBelow, disenchantBelow, useCurrencyMythic, useCoin)
			if loot["value"] <= upgradeBelow:
				if loot["upgradeEssenceValue"] == 0:
					getHexCraft(auth, loot["lootName"], "redeem") #可直接兌換的才行，否則會變租用
				else:
					getHexCraft(auth, [loot["lootName"],"CURRENCY_champion"], "CHAMPION_upgrade")
				return getLoot(auth, ownChamps, upgradeBelow, disenchantBelow, useCurrencyMythic, useCoin)
		elif loot["displayCategories"] == "SKIN":
			count_OE += loot["disenchantValue"] * loot["count"]
		elif loot["displayCategories"] == "ETERNALS" or loot["displayCategories"] == "WARDSKIN":
			count_OE += loot["disenchantValue"] * loot["count"]			
	return {"champs":champList, "skins":skinList, "BE":count_be, "OE":count_OE, "ownOE":own_OE }

def getHexCraft(auth, lootId, recipeName, repeat=1):
	url = auth + f"/lol-loot/v1/recipes/{recipeName}/craft?repeat={repeat}"
	if recipeName == "redeem" :
		url = auth + "/lol-loot/v1/player-loot/{lootName}/redeem".format(lootName=lootId)
	res = requests.post(url, verify=False, json=lootId).json()
	#lootType = "added" if resJson["added"] else "redeemed"
	#lootType = "redeemed" if recipeName in ["redeem", "CHAMPION_upgrade", "CHEST_114_OPEN", "CHEST_187_OPEN"] else lootType
	if 'removed' in res.keys():
		try:
			removeds = [ removed['playerLoot'] for removed in res["removed"]]
			removeds = [ removed['localizedName'] if removed['localizedName'] else (removed['itemDesc'] if removed['itemDesc'] else removed['lootName'] ) for removed in removeds]
			#removedLoot = res["removed"][0]['playerLoot']
			#removed = removedLoot['localizedName'] if removedLoot['localizedName'] else (removedLoot['itemDesc'] if removedLoot['itemDesc'] else removedLoot['lootName'] )
			addedLoot = res['added'] + res['redeemed']
			addeds = [ f"{item['deltaCount']}個{item['playerLoot']['localizedName']}" if item['playerLoot']['localizedName'] else (f"{item['playerLoot']['itemDesc']}" if item['playerLoot']['itemDesc'] else f"{item['deltaCount']}個{item['playerLoot']['lootName']}") for item in addedLoot ]
		except Exception as e:
			print(e)
			printJSON(res)

		printLog("  已使用 {}個{} 兌換 {} ".format(res["removed"][0]["deltaCount"], "&".join(removeds), ", ".join(addeds)))

def getRecipes(auth, item, printUrl=False):
	url = auth + f"/lol-loot/v1/recipes/initial-item/{item}"
	if printUrl: print(url)
	res = requests.post(url, verify=False).json()
	return res

def getRanked(auth):
	url = auth + "/lol-ranked/v1/current-ranked-stats"
	resJson = requests.get(url, verify=False).json()
	tierDict = {"IRON":"灰鐵", "BRONZE":"青銅", "SILVER":"白銀", "GOLD":"黃金", "PLATINUM":"白金", "DIAMOND":"鑽石", "GRANDMASTER":"宗師", "MASTER":"大師", "CHALLENGER":"菁英"}
	divDict = {"V":5, "IV":4, "III":3, "II":2, "I":1, "NA":''}
	if "highestRankedEntry" in resJson.keys():
		#solo = resJson["highestRankedEntry"]
		solo = resJson["queueMap"]["RANKED_SOLO_5x5"]
		tier = "{}{}".format(solo["tier"][0], divDict[solo["division"]]) if solo["tier"] != "NONE" else ""
		info = "{} {}/{}".format(tier, solo["wins"], solo["losses"]) if tier else ""
		info1 = "{}{} ({}LP) {}W/{}L".format(tierDict[solo['tier']], divDict[solo["division"]], solo["leaguePoints"], solo["wins"], solo["losses"]) if tier else ""
		info2 = "{}({})".format(tier, solo["leaguePoints"]) if tier else ""
		return {"info1":info, "info1":info1, "info2":info2, "wins":solo["wins"], "losses":solo["losses"], "tier":tier}
def getRankedByName(auth, name):
	profile = getProfile(auth, name)
	if not profile:
		return f"  此召喚師不存在：{name}"
	url = f"{auth}/lol-ranked/v1/ranked-stats/{profile['puuid']}"
	resJson = requests.get(url, verify=False).json()
	tierDict = {"IRON":"灰鐵", "BRONZE":"青銅", "SILVER":"白銀", "GOLD":"黃金", "PLATINUM":"白金", "DIAMOND":"鑽石", "GRANDMASTER":"宗師", "MASTER":"大師", "CHALLENGER":"菁英"}
	divDict = {"V":5, "IV":4, "III":3, "II":2, "I":1, "NA":''}
	if "queueMap" in resJson.keys():
		solo = resJson["queueMap"]["RANKED_SOLO_5x5"]
		profile['solo'] = f"{tierDict[solo['tier']]}{divDict[solo['division']]} ({solo['leaguePoints']}LP)" if solo["tier"] != "NONE" else ""
		solo = resJson["queueMap"]["RANKED_FLEX_SR"]
		profile['flex'] = f"{tierDict[solo['tier']]}{divDict[solo['division']]} ({solo['leaguePoints']}LP)" if solo["tier"] != "NONE" else ""

		return profile


def getParser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", "--folder", default="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
	parser.add_argument("-t", "--token",  default="")
	return parser

def main():
	parser = getParser()
	args = parser.parse_args()

	List = [datetime.datetime.today().strftime("%Y%m%d")]
	if not os.path.exists("LCU.db"):
		sql.init("LCU.db", "Data")

	auth = getAuth2()
	auth = getAuth(args.dir) if not auth else auth
	info = getSummoner(auth)
	session = getSession(auth)
	idToken, acId = session['idToken'], session['accountId']

	try:
		evt = eventShop(auth)
		res = evt.purchaseOffer(target='隨機英雄碎片', maxToken=300)
		if res:
			printLog(f"  已使用 {res['cost']}個{res['tokenName']} 兌換 {res['count']}個{res['target']}")
	except Exception as e:
		pass

	store.buy1Icons(idToken, acId)
	loots = getLoot(auth, ownChamps=getChampion(auth)["allId"], upgradeBelow=0, disenchantBelow=0,
		useCurrencyMythic=20, useCoin=100, useCoinCURRENCY=0)
	champs = getChampion(auth)
	skins = getSkin(auth, info["summonerId"])
	wallet = getWallet(auth)
	ranked = getRanked(auth)

	text1 =  "ID：__{}__\tLV：{}\tRP：{}\n藍粉：{}+{}={}（含碎片分解）\t橘粉：{}+{}={}（含碎片分解）\n".format(info["name"], info["level"], 
		wallet["rp"], wallet["ip"], loots["BE"], wallet["ip"]+loots["BE"], loots["ownOE"], loots["OE"], loots["ownOE"]+loots["OE"])
	text1 += "牌位：{}\n\n".format(ranked["info1"]) if ranked["info1"] else "\n"
	text1 += "**英雄(共{:>2d}個)**：*{}*\n".format(len(champs["all"]), "/".join(champs["all"])) 
	text1 += "英雄(略)：*{}*\n".format("/".join(champs["simple"]) )
	text1 += "**造型(共{:>2d}個)**：*{}*\n".format( len(skins), "/".join(skins) )
	text1 += "**英雄碎片(共{:>2d}個)**：*{}*\n".format(len(loots["champs"]), "/".join(loots["champs"]) )
	text1 += "**造型碎片(共{:>2d}個)**：*{}*\n".format(len(loots["skins"]), "/".join(loots["skins"]) )

	text2 =  "{}\t{}\t".format(info["name"], info["level"] )
	text2 += "{}\t{}\t{}\t{}\t{}\t{}\t".format(wallet["rp"], wallet["ip"], loots["ownOE"]+loots["OE"], len(champs["all"]), len(skins), ranked["info2"] )
	text2 += "BE+{}={}/{}".format(loots["BE"], wallet["ip"]+loots["BE"] , ",".join(champs["simple"]) )
	
	print(text1, text2, sep="\n\n")
	text1 = text1.replace("*", "").replace("_", "")
	#print(text1, text2, sep="\n\n")

	List += [info['accountId'], info['name'], info["level"], wallet["rp"], wallet["ip"], wallet["ip"]+loots["BE"], loots["ownOE"], loots["ownOE"]+loots["OE"]]
	List += [len(champs["all"]), len(skins), "/".join(champs["all"]), "/".join(champs["simple"]), "/".join(skins), "/".join(loots["champs"]), "/".join(loots["skins"])]
	List += [text1, text2]
	
	sql.input("LCU.db", "Data", List, replace=True)

if __name__ == '__main__':
	auth = getAuth2(sucPrint=False)
	auth = getAuth("C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs", sucPrint=False) if not auth else auth

	#accessAllFriendRequests(auth)

	deleteFriend(auth, "")
	deleteFriendsByList(auth, loadFriendList("friend4.txt"))
	
	#deleteAllFriends(auth)
	#cleanAllFriendRequests(auth)

	import dailylogin
	dailylogin.main(multi=False)

	main()
	
	print()
