import os, re, time
import requests, json
import argparse
import lcu 

requests.packages.urllib3.disable_warnings()
header = {	"User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/11.15.388.2387 (CEF 74) Safari/537.36",
			"Content-Type": 'application/json'}
errDic = {
		'ERROR__SERVER_ERROR': '系統忙碌中，請稍後再試。',
		'ERROR__SELF_INVITATION_CODE': '不能輸入自己的邀請碼喔！',
		'ERROR__UNDER_MAINTENANCE': '活動維護中，請稍後再試',
		'ERROR__ALREADY_CLAIMED': '你已經兌換過此獎勵了！',
		'ERROR__PROVIDE_LIMIT': '你已經放五張懸賞令到兌換區了，要等待朋友領取後才能繼續放喔！',
		'ERROR__WRONG_INVITATION_CODE': '無效的邀請碼',
		'ERROR__INVITER_LIMIT': '你手慢囉，你的好友已經邀請五位好友了，快去跟其他朋友要邀請碼吧！',
		'ERROR__INVITEE_LIMIT': '你的朋友真多，你已經邀請五位好友了，把機留給別人吧！',
		'ERROR__ALREADY_BIND': '你已經用過此邀請碼囉！',
		'ERROR__OUT_OF_QUOTA': '你的懸賞令領取次數不足，請先把你多餘的懸賞令送給朋友吧！',
		'ERROR__NOT_EVENT_PERIOD': '非活動時間',
		'ERROR__CANT_CLAIM_INVITER': '你需要找更多朋友輸入你的邀請碼才能領取此獎勵！',
		'ERROR__CANT_CLAIM_INVITEE': '你需要輸入更多的邀碼才能領取此獎勵！',
	}

def printLog(text, end="\n"):
	print(text, end=end)
	with open("login.log","a", encoding = 'utf8') as data:
		data.write(str(text)+end)
def getToken(folder="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs", sucPrint=True, errPrint=True, multi=False):
	if os.path.isdir(folder):
		tokenList =[]
		for file in sorted(os.listdir(folder),reverse=True):
			reLog = re.match(r'.+?_LeagueClientUx\.log', file)
			if reLog:
				try:
					with open("{}\\{}".format(folder,file), 'r', encoding="utf-8") as data:
						reToken = re.search(r'https://.+?\.lol\.garena\.tw/.+?token=(.{64})\"', data.read())
				except:
					with open("{}\\{}".format(folder,file), 'r', errors="ignore") as data:
						reToken = re.search(r'https://.+?\.lol\.garena\.tw/.+?token=(.{64})\"', data.read())
				if reToken:
					token = reToken.group(1)
					print("已從LOL安裝路徑獲取token：{}".format(reToken.group(1))) if sucPrint else print(end="")
					if not multi: return reToken.group(1) 
					elif token not in tokenList: tokenList.append(token)
		if len(tokenList) > 0 : return tokenList 
	print("錯誤：無法從LOL安裝路徑獲取token，請嘗試輸入安裝路徑或手動獲取token。") if errPrint else print(end="")
	return False
def getProfile(token):
	url = "https://findmymap.lol.garena.tw/api/profile"
	header['Referer'] = "https://findmymap.lol.garena.tw/?token={}".format(token)
	header['token'] = token
	try:
		res = requests.get(url, headers=header).json()
	except:
		print(" Error: connect error, getProfile again!")
		time.sleep(0.5)
		return getProfile(token)
	return res if ('error' not in res) else False
def bind(token, code, debug=False):
	url = "https://findmymap.lol.garena.tw/api/bind"
	header['Referer'] = "https://findmymap.lol.garena.tw/?token={}".format(token)
	header['token'] = token
	data = {'invitation_code': code, 'confirm':False}
	try:
		res = requests.post(url, headers=header, json=data)
		data['confirm'] = True
		res = requests.post(url, headers=header, json=data).json()
	except:
		print(" Error: connect error, bind again!")
		time.sleep(0.5)
		return bind(token, code, debug)
	if 'error' not in res.keys():
		print("  輸入 {} 的邀請碼成功".format(res['inviter']))
		return res
	elif debug:
		if res['error'] in errDic: print(errDic[res['error']])
		else: print(res['error'])
	return False
def claim(token, debug=False):
	url = "https://findmymap.lol.garena.tw/api/claim"
	header['Referer'] = "https://findmymap.lol.garena.tw/?token={}".format(token)
	header['token'] = token
	profile = getProfile(token)
	for ctype in range(2):
		start = len(profile['profile']['claimed_inviter_reward'])+1 if ctype==0 else len(profile['profile']['claimed_invitee_reward'])+1
		end = len(profile['invitation']['inviter'])+1 if ctype==0 else len(profile['invitation']['invitee'])+1
		for order in range(start,end):
			data = {"claim_type": ctype, "order": order}
			try:
				res = requests.post(url, headers=header, json=data)
			except:
				print(" Error: connect error, claim again!")
				time.sleep(0.5)
				return claim(token, debug)
			resJson = json.loads(res.text)
			if 'error' not in resJson.keys():
				items = [item['item_name'] for item in resJson['reward']]
				print("  已獲得 {} ".format("、".join(items)))
			elif debug:
				if resJson['error'] in errDic: print(errDic[resJson['error']])
				else: print(resJson['error'])
def provide(token, provideAll=False, debug=False):
	url = "https://findmymap.lol.garena.tw/api/provide"
	header['Referer'] = "https://findmymap.lol.garena.tw/?token={}".format(token)
	header['token'] = token
	owned = getProfile(token)['profile']['owned_fragment']
	for order in owned:
		if owned[order] < (1 if provideAll else 2): continue
		data = {"order": int(order)}
		for i in range(owned[str(order)]-(0 if provideAll else 1)):
			try:
				res = requests.post(url, headers=header, json=data).json()
			except:
				print(" Error: connect error, provide again!")
				time.sleep(0.5)
				return provide(token, provideAll, debug)
			time.sleep(0.5)
			if 'error' not in res.keys():
				print("  提供 {} 碎片成功，目前已提供 {} 碎片".format(order, str(res['profile']['provide_fragment'])))
			elif debug:
				if res['error'] in errDic: print(errDic[res['error']])
				else: print(res['error'])
def getFragments(token):
	url = "https://findmymap.lol.garena.tw/api/fragments"
	header['Referer'] = "https://findmymap.lol.garena.tw/?token={}".format(token)
	header['token'] = token
	try:
		res = requests.get(url, headers=header).json()
	except:
		print(" Error: connect error, getFragments again!")
		time.sleep(0.5)
		return getFragments(token)
	return res if ('error' not in res) else False
def receive(token, debug=False):
	url = "https://findmymap.lol.garena.tw/api/receive"
	header['Referer'] = "https://findmymap.lol.garena.tw/?token={}".format(token)
	header['token'] = token
	res = getFragments(token)
	fragments = res['fragments']
	quota = res['profile']['receive_quota']
	friends = loadFriendList()

	for order in fragments:
		for frag in fragments[order]:
			if quota <= 0 : return True
			if frag['summoner_name'] in friends:
				data = {"provider": frag['garena_uid'], "order": int(order)}
				try:

					res = requests.post(url, headers=header, json=data).json()
				except:
					print(" Error: connect error, receive again!")
					time.sleep(0.5)
					return receive(token, debug)
				time.sleep(0.5)
				if 'error' not in res.keys():
					print("  獲取 {} 的 {} 碎片成功".format(frag['summoner_name'], order))
					quota -= 1
				elif debug:
					if res['error'] in errDic: print(errDic[res['error']])
					else: print(res['error'])

def getErrDic():
	url = "https://rosetta-tw.garenanow.com/transify/1770?lang=2"
	header = {"Referer": "https://findmymap.lol.garena.tw"}
	res = requests.get(url, headers=header)
	res.encoding = 'utf8'
	resJson = json.loads(res.text)
	print(resJson)

def loadDict(filename="code.txt"):
	if os.path.exists(filename):
		with open(filename , "r", encoding = 'utf-8-sig') as data:
			Dict = {line.strip().split("\t")[0]:int(line.strip().split("\t")[1]) for line in data }
	else: Dict = {}
	return Dict
def saveDict(Dict, filename="code.txt", saveNum=5):
	with open(filename, "w", encoding = 'utf-8-sig') as data:
		for key in Dict.keys():
			if int(Dict[key]) < saveNum :
				data.write("{}\t{}\n".format(key, Dict[key]))

def loadFriendList(filename="friends.txt"):
	if os.path.exists(filename):
		with open(filename , "r", encoding = 'utf-8-sig') as data:
			friendList = [ line.strip() for line in data ]
	else: friendList = []
	return friendList
def getParser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", "--folder", default="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
	#parser.add_argument("-d", "--dir", "--folder", default="D:\\32775\\Game\\Logs\\LeagueClient Logs")
	parser.add_argument("-t", "--token",  default="")
	return parser

def findMyMap():

	tokens = getToken(args.dir, multi=True, sucPrint=False)
	while(not tokens):
		path = input("請輸入LeagueClient Logs之路徑：\n ")
		tokens = getToken(path, multi=True)

	codeDict = loadDict(filename="code.txt")
	tokenDict = loadDict(filename="token.txt")
	for token in tokens:
		if token not in tokenDict.keys():
			tokenDict[token] = 0

	for token in tokens[:8]*2: #互相輸入區
		profile = getProfile(token)
		if not profile: continue
		if tokenDict[token] >= 10: continue
		if len(profile['profile']['claimed_inviter_reward']) +len(profile['profile']['claimed_invitee_reward']) >= 10: continue
		print(token)
		mycode = profile['profile']['invitation_code']
		codeDict[mycode] = len(profile['invitation']['invitee']) #紀錄已使用次數
		count = len(profile['invitation']['inviter'])
		for code in codeDict.keys():
			if count == 5: break
			if mycode == code: continue
			res = bind(token, code)
			time.sleep(1)
			codeDict[code] += (1 if res else 0)
			count += (1 if res else 0)
		claim(token) #兌換獎勵
		provide(token) #提供碎片
		#provide(token, provideAll=True)
		profile = getProfile(token)
		tokenDict[token] = len(profile['profile']['claimed_inviter_reward']) +len(profile['profile']['claimed_invitee_reward'])
		saveDict(codeDict, filename="code.txt", saveNum=5)

	for token in tokenDict:
		profile = getProfile(token)
		if not profile:
			tokenDict[token] = 99
			continue
		print(token)
		try:
			receive(token)
			provide(token)
			receive(token)
		except:
			pass
		#tokenDict[token] = getProfile(token)['profile']['receive_quota']

	saveDict(codeDict, filename="code.txt", saveNum=5)
	saveDict(tokenDict, filename="token.txt", saveNum=77)

if __name__ == '__main__':
	global args
	parser = getParser()
	args = parser.parse_args()

	findMyMap()
	exit()
