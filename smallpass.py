import os, re, time
import requests, json
import argparse

requests.packages.urllib3.disable_warnings()
#UA = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/11.18.388.2387 (CEF 74) Safari/537.36"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
def printLog(text, end="\n"):
	print(text, end=end)
	with open("login.log","a", encoding = 'utf8') as data:
		data.write(str(text)+end)
def getErrDic():
	url = "https://rosetta-tw.garenanow.com/transify/2638?lang=2"
	header = {"Referer": "https://wintoken.lol.garena.tw"}
	res = requests.get(url, headers=header)
	res.encoding = 'utf8'
	resJson = json.loads(res.text)
	return {info if info.startswith("ERROR") else "" :resJson[info]  for info in resJson.keys()}
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
def getToken(folder, sucPrint=True, errPrint=True, multi=False):
	if os.path.isdir(folder):
		tokenList =[]
		for file in sorted(os.listdir(folder),reverse=True):
			reLog = re.match(r'.+?_LeagueClientUx\.log', file)
			if reLog:
				try:
					with open("{}\\{}".format(folder,file), 'r', encoding="utf-8") as data:
						reToken = re.search(r'https://.+?\.lol\.garena\.tw/.+?token=(.+)\"', data.read())
				except:
					with open("{}\\{}".format(folder,file), 'r', errors="ignore") as data:
						reToken = re.search(r'https://.+?\.lol\.garena\.tw/.+?token=(.+)\"', data.read())
				if reToken:
					token = reToken.group(1)
					print("已從LOL安裝路徑獲取token：{}".format(reToken.group(1))) if sucPrint else print(end="")
					if not multi: return reToken.group(1) 
					elif token not in tokenList: tokenList.append(token)
		if len(tokenList) > 0 : return tokenList 
	print("錯誤：無法從LOL安裝路徑獲取token，請嘗試輸入安裝路徑或手動獲取token。") if errPrint else print(end="")
	return False
def getProfile(token):
	url = "https://smallpass.lol.garena.tw/api/profile"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://smallpass.lol.garena.tw/?token={}".format(token),
				"token": token,
			}
	res = requests.get(url, headers=header)
	resJson = json.loads(res.text)
	return resJson if ('error' not in resJson) else False
def drawPass(token):
	url = "https://smallpass.lol.garena.tw/api/draw"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://smallpass.lol.garena.tw/?token={}".format(token),
				"sso-token":token,
				"token": token,
			}
	profile = getProfile(token)
	if not profile['free_remain_time']:
		data = {'cost': 0, 'draw_type': 0}
		res = requests.post(url, headers=header, data=json.dumps(data))
		resJson = json.loads(res.text)
		if 'error' not in resJson.keys():
			profile = getProfile(token)
			printLog("UID：{}\t當前等級：{}\t經驗：{}".format(profile['uid'], profile['level'], profile['experience']))
			rewards = [reward['name'] for reward in resJson['receive_rewards']]
			printLog("  已獲得基金獎勵：{}".format("、".join(rewards)))
			return True
		elif 'error' not in profile.keys():
			print("UID：{}\t當前等級：{}\t經驗：{}".format(profile['uid'], profile['level'], profile['experience']))
			return True
		elif debug:
			if resJson['error'] in errDic: print(errDic[resJson['error']])
			else: print(resJson['error'])
	return False
def getParser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", "--folder", default="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
	#parser.add_argument("-d", "--dir", "--folder", default="D:\\32775\\Game\\Logs\\LeagueClient Logs")
	parser.add_argument("-t", "--token",  default="")
	return parser
def main():
	global args
	parser = getParser()
	args = parser.parse_args()

	tokens = getToken(args.dir, multi=True, sucPrint=False)
	while(not tokens):
		path = input("請輸入LeagueClient Logs之路徑：\n ")
		tokens = getToken(path, multi=True)
	tokenDict = loadDict(filename="token.txt")

	for token in tokens:
		if token not in tokenDict: tokenDict[token] = 0

	for token in tokenDict:
		profile = getProfile(token)
		if not profile:
			tokenDict[token] = 999
			continue
		if profile['free_remain_time']: 
			tokenDict[token] = profile['free_remain_time']//3600*10 + 10
			continue
		print(token)
		drawPass(token)
		time.sleep(1)
		
	#print(tokenDict)
	saveDict(tokenDict, filename="token.txt", saveNum=800)

if __name__ == '__main__':
	errDic = getErrDic()
	main()