import os, re, time
import requests, json
import argparse
from datetime import datetime

requests.packages.urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/11.18.388.2387 (CEF 74) Safari/537.36"

STARTDATE = [5, 13]

def printLog(text, file="hexparty.log", end="\n"):
	print(text, end=end)
	with open(file, "a", encoding = 'utf8') as data:
		data.write(str(text)+end)
def printJSON(data):
	print(json.dumps(data, ensure_ascii=False, indent=4))
def getErrDic():
	url = "https://rosetta-tw.garenanow.com/transify/3148?lang=2"
	header = {"Referer": "https://hexparty.lol.garena.tw"}
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
	url = "https://hexparty.lol.garena.tw/api/profile"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://hexparty.lol.garena.tw/?token={}".format(token),
				"token": token,
			}
	res = requests.get(url, headers=header)
	if res.status_code != 200:
		print(f"  Server Error: {res.status_code}")
		return res.status_code
	resJson = json.loads(res.text)
	return resJson if ('error' not in resJson) else False
def claimLoginReward(token, debug=False):
	url = "https://hexparty.lol.garena.tw/api/claim-login-reward"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://hexparty.lol.garena.tw/?token={}".format(token),
				"token": token,
			}
	success, rewards = [], []
	profile = getProfile(token)
	for period in profile['login_mission_periods']:
		for reward in period['rewards']:
			if reward['status'] != 1 : continue
			data = {'id': reward['id']}
			res = requests.post(url, headers=header, json=data).json()
			if 'reward' in res.keys():
				success.append(str(reward['id']))
				rewards.append(res['reward']['reward_name'])
			elif debug:
				if res['error'] in errDic: print(errDic[res['error']])
				else: print(res['error'])
			time.sleep(0.1)
	if success:		printLog("  已兌換第 {} 天登入獎勵：{}".format(", ".join(success), "、".join(rewards)))
	time.sleep(0.5)
	return int(success[-1]) if success else 999
def claimMilestone(token, debug=False):
	url = "https://hexparty.lol.garena.tw/api/claim-milestone"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://hexparty.lol.garena.tw/?token={}".format(token),
				"token": token,
			}
	success, rewards = [], []
	profile = getProfile(token)
	for reward in profile['milestones']:
		if reward['status'] != 1 : continue
		data = {'milestone_id': reward['id']}
		res = requests.post(url, headers=header, json=data).json()
		if 'reward' in res.keys():
			success.append(str(reward['id']))
			rewards.append(res['reward']['reward_name'])
		elif debug:
			if res['error'] in errDic: print(errDic[res['error']])
			else: print(res['error'])
		time.sleep(0.1)
	if success:		printLog("  已兌換里程碑獎勵：{}".format("、".join(rewards)))
	time.sleep(0.5)
	return int(success[-1]) if success else 999
def purchaseLogin(token, debug=False): #補簽到
	url = "https://hexparty.lol.garena.tw/api/purchase-login"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://hexparty.lol.garena.tw/?token={}".format(token),
				"token": token,
			}
	profile = getProfile(token)
	for i in range(profile['purchase_login']['free_remaining']):
		res = requests.post(url, headers=header).json()
		if 'error' not in res.keys():
			print("  已補簽到")
	return
def ClaimLoginTopPrize(token, maxStar=99, debug=False):
	url = "https://hexparty.lol.garena.tw/api/claim-login-top-prize"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://hexparty.lol.garena.tw/?token={}".format(token),
				"token": token,
			}
	profile = getProfile(token)
	stars_gain = 0
	for period in profile['login_mission_periods']:
		for reward in period['rewards']:
			if reward['status'] == 2 : stars_gain +=1
	stars_gain = stars_gain if stars_gain <= maxStar else maxStar
	data = {'login_top_prize_id': stars_gain}
	res = requests.post(url, headers=header, json=data).json()
	if 'reward' in res.keys():
		printLog(f"  已兌換 {stars_gain}星 累積獎勵：{res['reward']['reward_name']}")
	elif debug:
		if res['error'] in errDic: print(errDic[res['error']])
		else: print(res['error'])
	return 

def getParser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", "--folder", default="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
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
		elif isinstance(profile, int):
			continue
		if tokenDict[token] >= time.localtime().tm_mday-STARTDATE[1]+1 or tokenDict[token]==14: continue
		for period in profile['login_mission_periods']:
			for reward in period['rewards']:
				if reward['status'] == 2 : tokenDict[token] = reward['id']
		if tokenDict[token] >= time.localtime().tm_mday-STARTDATE[1]+1 or tokenDict[token]==14: continue
		printLog(token)
		purchaseLogin(token)
		claimMilestone(token)
		tokenDict[token] = claimLoginReward(token)
		ClaimLoginTopPrize(token, maxStar=5)
		time.sleep(1)
		
	#print(tokenDict)
	saveDict(tokenDict, filename="token.txt", saveNum=800)

errDic = getErrDic()

if __name__ == '__main__':

	main()