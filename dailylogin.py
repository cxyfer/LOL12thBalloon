import os, re, time
import requests, json
import argparse
from datetime import datetime

from auth import *

requests.packages.urllib3.disable_warnings()

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
tonow = datetime.now()

def printLog(text, level="INFO", end="\n"):
	text = f"{level:>6s} | {text}"
	print(text)
	with open("dailywheel.log","a", encoding = 'utf8') as data:
		data.write(str(text)+end)
def printJSON(data):
	print(json.dumps(data, ensure_ascii=False, indent=4))
def getErrDic(aid=3558, refer="https://couponqueen.lol.garena.tw/"):
	url = "https://rosetta-tw.garenanow.com/transify/{}?lang=2".format(aid)
	header = {"Referer": refer}
	res = requests.get(url, headers=header)
	res.encoding = 'utf8'
	resJson = json.loads(res.text)
	return {info if info.startswith("ERROR") else "" :resJson[info]  for info in resJson.keys()}

class dailyLogin():
	def __init__(self, token):
		self.token = token
		self.header = {	"User-Agent": UA,
						"Content-Type": 'application/json',
						"Referer": f"https://dailylogin.lol.garena.tw/?token={token}",
						"token": token, 
					}
		self.getInfo(token)
	def getInfo(self, token, dataPrint=False):
		url = f"https://dailylogin.lol.garena.tw/api/info?token={token}"
		res = requests.get(url, headers=self.header)
		self.header["x-csrftoken"] = dict(res.cookies)['csrftoken']
		self.cookies = res.cookies
		self.info = res.json()

		if dataPrint:
			for i in range(14):
				print("第{:>2d}天登入領取：{}".format(i+1, self.info["login_rewards"][i]["name"]))
				print("　　　額外獎勵：{:>4d} {} 兌換 {}".format( self.info["missions"][i]["price"],res["missions"][i]["type"].upper(),res["mission_bonuses"][i]["name"]))
	def receive(self, token, day=0, redeem=False): #免費領取
		url = "https://dailylogin.lol.garena.tw/api/receive" if not redeem else "https://dailylogin.lol.garena.tw/api/redeem"
		data = {'day': day}
		res = requests.post(url, headers=self.header, data=json.dumps(data), cookies=self.cookies)
		if res.status_code==200:
			resJson = res.json()
			if 'actual_name' in resJson.keys():
				printLog("  已兌換獎勵：{}".format(resJson['actual_name']))
				time.sleep(0.25)
			elif 'error' in resJson.keys():
				if resJson['error'] != 'COMMON': printLog(resJson['error'])
			return resJson
	def supplement(self, token): #補簽
		url = "https://dailylogin.lol.garena.tw/api/supplement"
		res = requests.post(url, headers=self.header, cookies=self.cookies)
		if res.status_code==200:
			resJson = res.json()
			if 'supplemented_date' in resJson.keys():
				timestamp = resJson['supplemented_date']
				timeString = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
				printLog("  已補簽到：{}".format(timeString))
			else:
				return False
	def couponqueen(self, token):
		header['Referer'] = "https://couponqueen.lol.garena.tw/?token={}".format(token)
		header['sso-token'] = token
		url = "https://couponqueen.lol.garena.tw/api/profile"
		res = requests.get(url, headers=header)
		if 'error' in res.json():
			print(errDic[res.json()['error']])
			return False
		#header["x-csrftoken"] = dict(res.cookies)['csrftoken']
		profile = res.json()['profile']
		if profile['wheel_active_index'] != -1:
			return False
		else:
			url = "https://couponqueen.lol.garena.tw/api/spin"
			res = requests.post(url, headers=header, cookies=res.cookies).json()['profile']
			results = ["75折","45折","85折","1元","9折","3折"]
			print(f"  一元特賣抽獎結果：{results[res['wheel_active_index']]}")
			if res['wheel_active_index'] == 3: #1元
				print("  可選獎項：", end="")
				print(" & ".join([reward['name'] for reward in profile['grid']]))
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
def getLog(keyList, filename="lcu.log"):
	if isinstance(keyList, str): keyList = [keyList]
	with open(filename , "r", encoding = 'utf-8-sig') as data:
		for line in data:
			for key in keyList:
				if key in line:
					print(line.strip())
					break
			

def getParser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", "--folder", default="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
	#parser.add_argument("-d", "--dir", "--folder", default="D:\\32775\\Game\\Logs\\LeagueClient Logs")
	parser.add_argument("-t", "--token",  default="")
	return parser
def main(multi=True):
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
	countDay = time.localtime().tm_mday
	for token in tokenDict.keys():
		if tokenDict[token] > countDay-16 or tokenDict[token] >= 14:
			continue
		obj = dailyLogin(token)
		if "logined" not in obj.info.keys(): 
			if obj.info["error"] == 'LOGIN_FAILED': #LOGIN_FAILED
				tokenDict[token] = 99
				continue
			else:
				printJSON(obj.info)
		print(token)
		#couponqueen(token)
		for day in range(14):
			if obj.info['login_rewards'][day]['received_date']:
				tokenDict[token] = day+1
				continue
			if obj.info["logined"][day]:
				obj.receive(token, day=day)
				tokenDict[token] = day+1
			elif len(obj.info["supplemented_dates"]) < 4: #補簽到
				obj.supplement(token)
				obj.receive(token, day=day)
				obj.getInfo(token)
			if day in [4, 7, 9]:
				obj.receive(token, day=day, redeem=True)
		for day in [4, 7, 9]:
			obj.receive(token, day=day, redeem=True)

		if multi:
			saveDict(tokenDict, filename="token.txt", saveNum=1231)
	if not multi:
		tokenDict.update(loadDict(filename="token.txt"))
	saveDict(tokenDict, filename="token.txt", saveNum=70)
if __name__ == '__main__':

	main(multi=True)