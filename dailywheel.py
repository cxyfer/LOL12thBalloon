import os, re, time
import requests, json
import argparse
import random
from datetime import datetime

from auth import *

DATE = "1118"

requests.packages.urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
tonow = datetime.now()

def getErrDic():
	url = "https://rosetta-tw.garenanow.com/transify/3556?lang=2"
	header = {"Referer": "https://dailywheel.lol.garena.tw"}
	res = requests.get(url, headers=header)
	res.encoding = 'utf8'
	resJson = json.loads(res.text)
	return {info if info.startswith("ERROR") else "" :resJson[info]  for info in resJson.keys()}
def printJSON(data):
	print(json.dumps(data, ensure_ascii=False, indent=4))
def printLog(text, level="INFO", end="\n"):
	text = f"{level:>6s} | {text}"
	print(text)
	with open("dailywheel.log","a", encoding = 'utf8') as data:
		data.write(str(text)+end)
def mask(text, k=5):
	text, n = re.subn('|'.join(random.choices(text, k=k)), '#', text)
	if (n<len(text)/4):
		return mask(text, k=k+1)
	return text
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
	return friendList if os.path.exists(filename) else []


class dailyWheel():
	def __init__(self, token):
		self.token = token
		self.header = {	"User-Agent": UA,
						"Content-Type": 'application/json',
						#"Referer": f"https://dailywheel.lol.garena.tw/{tonow.month:02d}{tonow.day:02d}/?token={token}",
						"Referer": f"https://dailywheel.lol.garena.tw/{DATE}/?token={token}",
						"token": token, 
						"batch": f"{DATE}", # New Auth
					}
		self.profile = self.getProfile()

	def getProfile(self):
		url = "https://dailywheel.lol.garena.tw/api/profile"
		res = requests.get(url, headers=self.header)
		if res.status_code != 200:
			printLog(f"Server Error: {res.status_code}", "ERROR")
			return res.status_code
		else:
			return res.json() if ('error' not in res.json()) else False
	def draw(self, week_id, draw_type=0, debug=True):
		url = "https://dailywheel.lol.garena.tw/api/draw"
		data = {"week_id": week_id, "draw_type": draw_type, "draw_cost": 0} #draw_type 0:free 1:pay
		res = requests.post(url, headers=self.header, json=data).json()
		if 'reward' in res.keys():
			reward_type = "免費" if draw_type==0 else "付費"
			printLog(f"從{reward_type}轉盤獲得：{res['reward']['name']}", "INFO")
			if res['reward']['name'] == "黃金鑰匙":
				print(f"  Update profile...")
				self.profile = self.getProfile()
		elif debug:
			if res['error'] in errDic: printLog(errDic[res['error']], "DEBUG")
			else: printLog(res['error'], "DEBUG")

	def drawAll(self, debug=True):
		for i in range(4):
			for j in range(self.profile['weeks'][i]['free_draw_amount']):
				self.draw(i+1, debug=True)
			for j in range(self.profile['weeks'][i]['token_amount']):
				self.draw(i+1, draw_type=2, debug=True)
	def recheck(self, week_id, debug=True):
		url = "https://dailywheel.lol.garena.tw/api/recheck"
		data = {"week_id": week_id}
		res = requests.post(url, headers=self.header, json=data).json()
		if 'free_draw_amount' in res.keys():
			pass
		elif debug:
			if res['error'] in errDic: printLog(errDic[res['error']], "DEBUG")
			else: printLog(res['error'], "DEBUG")
	def recheckAll(self, debug=True):
		for i in range(4):
			for j in range(self.profile['weeks'][i]['recheck_available_amount']):
				self.recheck(i+1, debug=True)
		self.profile = self.getProfile()
	def printReward(self, debug=True):
		for week in self.profile['weeks']:
			print(f"W{week['week_id']} ({week['week_name']})")
			for reward in week['free_wheel_rewards']:
				print(reward['name'], end="、")
			print()
			for reward in week['pay_wheel_rewards']:
				print(reward['name'], end="、")
			print()
		exit()

def getParser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", "--folder", default="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
	parser.add_argument("-t", "--token",  default="")
	return parser

def main(multi=True, typeIdx=-1, skipDonate=0, debug=False):
	global args, errDic
	parser = getParser()
	args = parser.parse_args()

	errDic = getErrDic()
	# Read & Load token
	tokens = getToken(args.dir, multi=multi, sucPrint=False)
	while(not tokens):
		path = input("請輸入LeagueClient Logs之路徑：\n ")
		tokens = getToken(path, multi=multi)
	if multi:
		tokenDict = loadDict(filename="token.txt")
		for token in tokens:
			if token not in tokenDict: tokenDict[token] = 0
	else:
		tokenDict= {tokens:0}
	# Start
	if multi:
		printLog(f"{'-'*64}" ,"------")
		printLog(f"{tonow.year}/{tonow.month:02d}/{tonow.day:02d}" ,"TODAY")

	for token in tokenDict:
		if tokenDict[token] == int(f"{tonow.month:02d}{tonow.day:02d}"):
			continue
		obj = dailyWheel(token)
		#obj.printReward()
		if not obj.profile:
			tokenDict[token] = 1232
			continue
		elif isinstance(obj.profile, int):
			continue
		#printJSON(obj.profile)
		print(obj.token)
		obj.recheckAll()
		obj.drawAll()

		tokenDict[token] = int(f"{tonow.month:02d}{tonow.day:02d}")
		if multi:
			saveDict(tokenDict, filename="token.txt", saveNum=1231)
	if not multi:
		tokenDict.update(loadDict(filename="token.txt"))
	saveDict(tokenDict, filename="token.txt", saveNum=1231)

errDic = getErrDic()
friendList = loadFriendList()

if __name__ == '__main__':
	main(skipDonate=25)