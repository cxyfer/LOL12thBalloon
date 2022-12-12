import os, re, time
import requests, json
import argparse
import random
from datetime import datetime

from auth import *

remainNum = 0
maxDonateIdx, maxDonateNum = 60, 24

requests.packages.urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"

def getErrDic():
	url = "https://rosetta-tw.garenanow.com/transify/3715?lang=2"
	header = {"Referer": "https://fashionurf.lol.garena.tw"}
	res = requests.get(url, headers=header)
	res.encoding = 'utf8'
	resJson = json.loads(res.text)
	return {info if info.startswith("ERROR") else "" :resJson[info]  for info in resJson.keys()}
def printJSON(data):
	print(json.dumps(data, ensure_ascii=False, indent=4))
def printLog(text, level="INFO", end="\n"):
	text = f"{level:>6s} | {text}"
	print(text)
	with open("fashionurf.log","a", encoding = 'utf8') as data:
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
class fashionURF():
	def __init__(self, token):
		self.token = token
		self.header = {	"User-Agent": UA,
						"Content-Type": 'application/json',
						"Referer": "https://fashionurf.lol.garena.tw/?token={}".format(token),
						"token": token, }
		self.info = self.getInfo()
		# key_amount, left_donate_chance, parts_status
		self.collocation = False if not self.info else self.getCollocation()
		if self.info: self.getTasks()
		self.donateDict = {}
	def getInfo(self):
		url = "https://fashionurf.lol.garena.tw/api/info"
		res = requests.get(url, headers=self.header)
		if res.status_code != 200:
			printLog(f"Server Error: {res.status_code}", "ERROR")
			return res.status_code
		else:
			return res.json() if ('error' not in res.json()) else False
	def getCollocation(self):
		url = "https://fashionurf.lol.garena.tw/api/collocation"
		res = requests.get(url, headers=self.header)
		if res.status_code != 200:
			printLog(f"Server Error: {res.status_code}", "ERROR")
			return res.status_code
		else: 
			return res.json() if ('error' not in res.json()) else False

	def redeemKey(self, code="starguardian2022", debug=False):
		url = "https://fashionurf.lol.garena.tw/api/redeem"
		data = {'code': code}
		res = requests.post(url, headers=self.header, json=data).json()
		if 'amount' in res.keys():
			printLog(f"使用 {code} 兌換 {res['amount']} 把鑰匙", "INFO")
			self.collocation = self.getCollocation()
		elif debug:
			if res['error'] in errDic: printLog(errDic[res['error']], "ERROR")
			else: printLog(res['error'], "ERROR")
	def openBox(self, typeIdx=-1, debug=True):
		self.collocation = self.getCollocation()
		if self.collocation['key_amount'] <=0:
			return False
		countList = [part.count("OWNED")+part.count("DRESSED") for part in self.collocation['parts_status']]
		if not sum([part.count("NOTOWNED") for part in self.collocation['parts_status']]):
			printLog("已擁有當前可獲得的所有部件", "DEBUG")
			return False
		elif sum(countList) >= 60-remainNum:
			printLog("剩餘部件數量超過保留數量，略過開箱", "DEBUG")
			return False
		url = "https://fashionurf.lol.garena.tw/api/open"
		typeList = [ part['type'] for part in self.info['parts'] ]
		idxList = []
		# 從剩餘最少的開始開，如果相同則亂數決定
		countDict = { idx:part.count("NOTOWNED") for idx, part in enumerate(self.collocation['parts_status'])}
		weightList = [ 0 if i==typeIdx else 9 for i in range(6) ]
		byNum = sorted(countDict.items(), key=lambda x: (weightList[x[0]],x[1],random.randrange(10)), reverse=False)

		for idx, notOwnedCnt in byNum:
			countList = [part.count("OWNED")+part.count("DRESSED") for part in self.collocation['parts_status']]
			if sum(countList) >= 60-remainNum:
				printLog("剩餘部件數量超過保留數量，停止開箱", "DEBUG")
				break
			if notOwnedCnt:
				openNum = notOwnedCnt if self.collocation['key_amount'] > notOwnedCnt else self.collocation['key_amount']
				openNum = min([openNum, 60-remainNum-sum(countList)])
				if openNum <= 0:
					break
				data = {'type': typeList[idx]}
				for i in range(openNum):
					res = requests.post(url, headers=self.header, json=data).json()
					if 'id' in res.keys():
						idxList.append(str(res['id']))
					elif debug:
						if res['error'] in errDic: printLog(errDic[res['error']], "ERROR")
						else: printLog(res['error'], "ERROR")
			self.collocation = self.getCollocation()
		if idxList:
			countList = [part.count("OWNED")+part.count("DRESSED") for part in self.collocation['parts_status']]
			printLog(f"已獲得 {','.join(idxList)} ，當前已擁有 {sum(countList)} 個部件")
	def getDonateDict(self, debug=False):
		donateCnt, donateNum = 0, 0
		idxList = [idx for idx in range(1, 61) if idx % 10 != 1 and self.collocation['parts_status'][(idx-1)//10][(idx-1)%10] == "OWNED"]
		if maxDonateIdx<20: random.shuffle(idxList)
		for idx in idxList:
			url = f"https://fashionurf.lol.garena.tw/api/donable_friend?id={idx}"
			data = {'id': idx}
			try:
				res = requests.get(url, headers=self.header, json=data).json()
			except:
				continue
			if 'friends' not in res:
				printJSON(res)
				continue
			for friend in res['friends']:
				if friend['username'] not in self.donateDict:
					self.donateDict[friend['username']] = friend
					self.donateDict[friend['username']]['idx'] = []
				self.donateDict[friend['username']]['idx'] += [idx]
				donateNum += 1
			donateCnt += 1
			if donateCnt >= maxDonateIdx and donateNum >= maxDonateNum:
				print(donateCnt, donateNum)
				break

	def donate(self, debug=False):
		if not self.collocation['left_donate_chance']:
			return False
		url = "https://fashionurf.lol.garena.tw/api/donate"	
		self.getDonateDict()
		if not self.donateDict:
			printLog("無可贈送部件之好友" ,"DEBUG")
			return False
		# 在指定清單內的優先
		byFriend = [self.donateDict[friend] for friend in friendList if friend in self.donateDict]
		#byFriend = sorted(byFriend, key=lambda x: (len(x['idx']), x['uid']), reverse=False)
		'''if debug:
			printLog("DonateDict by friendList", "DEBUG")
			printJSON(byFriend)'''
		# 按缺少數量少的
		byNum = sorted(self.donateDict.values(), key=lambda x: (len(x['idx']), x['uid']), reverse=False)
		for friend in (byFriend + byNum):
			sucNum = 0
			leftNum = self.collocation['left_donate_chance']
			if not leftNum: break
			if not friend['idx']: break
			if debug:
				printLog(f"好友 {friend['username']} 未擁有部件：{','.join(str(i) for i in friend['idx'])}", "DEBUG")
			random.shuffle(friend['idx'])
			idxList = []
			for idx in friend['idx']:
				data = {'friend_uid': friend['uid'], 'id': idx}
				res = requests.post(url, headers=self.header, json=data).json()
				if 'error' not in res.keys():
					idxList.append(str(idx))
					sucNum += 1
					if sucNum >= leftNum: break
				else:
					if res['error'] in errDic: printLog(errDic[res['error']], "ERROR")
					elif debug: printLog(res['error'], "DEBUG")
			if idxList:
				printLog(f"已贈送給{friend['username']}：{','.join(idxList)}", "INFO")
			self.collocation = self.getCollocation()
	def dressAndShare(self, debug=True):
		url = "https://fashionurf.lol.garena.tw/api/dress"
		data = {'dressed': [1, 11, 21, 31, 41, 51], 'is_share': True}
		res = requests.post(url, headers=self.header, json=data).json()
		if 'error' not in res.keys():
			printLog("已更換裝扮及分享成功")
		elif debug:
			if res['error'] in errDic: printLog(errDic[res['error']], "ERROR")
			else: printLog(res['error'], "ERROR")
	def getTasks(self):
		url = "https://fashionurf.lol.garena.tw/api/task"
		res = requests.get(url, headers=self.header).json()
		self.tasks = res['tasks']
	def claimTask(self, debug=True):
		url = "https://fashionurf.lol.garena.tw/api/task"
		res = requests.get(url, headers=self.header).json()
		tasks = res['tasks']
		if tasks[0]['status'] == "UNCOMPLETE":
			self.dressAndShare()
			tasks = requests.get(url, headers=self.header).json()['tasks']
		claimList = []
		for task in tasks:
			if task['status'] == "CLAIMABLE":
				url = "https://fashionurf.lol.garena.tw/api/claim"
				data = {'type': "TASK", 'id': task['id'], 'reward_id': None}
				res = requests.post(url, headers=self.header, json=data).json()
				if 'name' in res.keys():
					claimList.append(res['name'])
				elif debug:
					if res['error'] in errDic: printLog(errDic[res['error']], "ERROR")
					else: printLog(res['error'], "ERROR")
		if claimList:
			printLog(f"已兌換任務獎勵：{'、'.join(claimList)}", "INFO")
	def claim(self, debug=True):
		url = "https://fashionurf.lol.garena.tw/api/claim"
		data = {'type': "PEAK", 'id': 1, 'reward_id': None}
		res = requests.post(url, headers=self.header, json=data).json()
		if 'name' in res.keys():
			printLog(f"已領取登入獎勵：{res['name']}", "INFO")
		data = {'type': "QUIZ", 'id': 1, 'reward_id': None}
		res = requests.post(url, headers=self.header, json=data).json()
		if 'name' in res.keys():
			printLog(f"已領取測驗獎勵：{res['name']}", "INFO")
	def getMission(self, debug=True, printInfo=False):
		url = "https://fashionurf.lol.garena.tw/api/mission"
		res = requests.get(url, headers=self.header).json()
		weightList = [7,8,1,1,1,5,7,8,6,6,7,5,6,9]
		self.missions = sorted(res['missions'], key=lambda x: (weightList[int(x['id'])-1],x['id']) , reverse=True)
		if printInfo:
			for mission in self.missions:
				print(f"任務 {mission['id']:<2d}：{mission['reward']['name']}，{mission['duration']//3600}小時")
	def startMission(self, debug=True):
		self.getMission()
		url1 = "https://fashionurf.lol.garena.tw/api/start_mission"
		url2 = "https://fashionurf.lol.garena.tw/api/claim"
		missionCnt = 0
		for mission in self.missions:
			if not mission['open_cd'] and mission['duration'] == mission['mission_cd']: #任務已開啟且未開始
				#if missionCnt == 3: continue #保留給812中午的任務14
				data = {'id': mission['id']}
				res = requests.post(url1, headers=self.header, json=data).json()
				if 'mission_cd' in res.keys():
					printLog(f"已開始任務{mission['id']}，剩餘時間{res['mission_cd']//3600}:{res['mission_cd']%3600:02d}", "INFO")
					missionCnt += 1
			elif not mission['mission_cd'] and not mission['claimed']: #任務已完成且未領取
				data = {'type': "MISSION", 'id': mission['id'], 'reward_id': None}
				res = requests.post(url2, headers=self.header, json=data).json()
				if 'name' in res.keys():
					printLog(f"已領取任務{mission['id']}獎勵：{res['name']}", "INFO")
			elif mission['mission_cd'] and mission['duration'] != mission['mission_cd']: # 正在進行任務
				missionCnt += 1
		#printLog(f"正在進行中的任務數量：{missionCnt}", "DEBUG")
	def couponqueen(self):
		header = dict(self.header)
		header['Referer'] = "https://couponqueen.lol.garena.tw/?token={}".format(self.token)
		header['sso-token'] = self.token
		url = "https://couponqueen.lol.garena.tw/api/profile"
		res = requests.get(url, headers=header)
		if 'error' in res.json():
			print(errDic[res.json()['error']]) if res.json()['error'] in errDic else print(res.json()['error']) 
			return False
		#header["x-csrftoken"] = dict(res.cookies)['csrftoken']
		profile = res.json()['profile']

		if profile['wheel_active_index'] == -1:
			url = "https://couponqueen.lol.garena.tw/api/spin"
			profile = requests.post(url, headers=header, cookies=res.cookies).json()['profile']
			results = ["75折","45折","85折","1元","9折","3折"]
			printLog(f"一元特賣抽獎結果：{results[profile['wheel_active_index']]}", "INFO")
		if profile['wheel_active_index'] == 3:
			printLog("可選獎項：" + ", ".join([reward['name'] for reward in profile['grid']]), "INFO")

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
	# Read & ;oad token
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
	tonow = datetime.now()
	if multi:
		printLog(f"{'-'*64}" ,"------")
		printLog(f"{tonow.year}/{tonow.month:02d}/{tonow.day:02d}" ,"TODAY")
	for token in tokenDict:
		if tokenDict[token] == int(f"{tonow.month:02d}{tonow.day:02d}"):
			continue
		obj = fashionURF(token)
		#obj.getMission()
		if not obj.info:
			tokenDict[token] = 1232
			continue
		elif isinstance(obj.info, int):
			continue
		tokenDict[token] = int(f"{tonow.month:02d}{tonow.day:02d}")

		#print(mask(token))
		printLog(f"{'-'*len(token)}", "------")
		printLog(f"{obj.info['username']}", "USER")

		obj.claim()
		obj.startMission()
		obj.couponqueen()
		if multi and not obj.collocation['left_donate_chance']: #跳過沒有贈送額度
			continue

		tasksStatus = [task['status'] for task in obj.tasks]
		if not (tasksStatus.count("UNCOMPLETE")+tasksStatus.count("CLAIMABLE")): #跳過已完成所有任務
			printLog(f"{obj.info['username']} 已完成所有任務", "DEBUG")
			continue
			#if multi: continue

		#ownIdxList = [ str(i*10+j) for i, part in enumerate(obj.collocation['parts_status']) for j, status in enumerate(part) if status=="OWNED" or status=="DRESSED"]
		countList = [part.count("OWNED")+part.count("DRESSED") for part in obj.collocation['parts_status']]
		printLog(f"當前已擁有 {sum(countList)} 個部件，剩餘鑰匙 {obj.collocation['key_amount']} 把，剩餘贈送次數 {obj.collocation['left_donate_chance']} 次", "INFO")

		obj.redeemKey()
		obj.redeemKey("SPECIALURF")
		obj.redeemKey("GODTONE777")
		obj.openBox(typeIdx=typeIdx)
		'''if skipDonate>=25 and obj.tasks[8]['status'] == "CLAIMED":
			printLog(f"已分享 25 個部件給朋友", "DEBUG")
			obj.donate(debug=debug)
		else:
			if skipDonate>=15 and obj.tasks[7]['status'] == "CLAIMED":
				printLog(f"已分享 15 個部件給朋友", "DEBUG")
			obj.donate(debug=debug)'''
		obj.claimTask()
		#tokenDict[token] = int(f"{tonow.month}{tonow.day}")
		if multi:
			saveDict(tokenDict, filename="token.txt", saveNum=1231)
		#time.sleep(1)
	if not multi:
		tokenDict.update(loadDict(filename="token.txt"))
	saveDict(tokenDict, filename="token.txt", saveNum=1231)

errDic = getErrDic()
friendList = loadFriendList()

if __name__ == '__main__':
	main(skipDonate=25)