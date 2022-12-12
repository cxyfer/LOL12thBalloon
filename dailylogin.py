import os, re, time
import requests, json
import argparse

requests.packages.urllib3.disable_warnings()

header = {	"User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/11.15.388.2387 (CEF 74) Safari/537.36",
			"Content-Type": 'application/json'}
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
def getErrDic(aid=3558, refer="https://couponqueen.lol.garena.tw/"):
	url = "https://rosetta-tw.garenanow.com/transify/{}?lang=2".format(aid)
	header = {"Referer": refer}
	res = requests.get(url, headers=header)
	res.encoding = 'utf8'
	resJson = json.loads(res.text)
	return {info if info.startswith("ERROR") else "" :resJson[info]  for info in resJson.keys()}
def getInfo(token, dataPrint=False):
	header['Referer'] = "https://dailylogin.lol.garena.tw/?token={}".format(token)
	url = "https://dailylogin.lol.garena.tw/api/info?token={}".format(token)
	res = requests.get(url, headers=header).json()

	if dataPrint:
		for i in range(14):
			print("第{:>2d}天登入領取：{}".format(i+1,res["login_rewards"][i]["name"]))
			print("　　　額外獎勵：{:>4d} {} 兌換 {}".format(res["missions"][i]["price"],res["missions"][i]["type"].upper(),res["mission_bonuses"][i]["name"]))
	return res
def receive(token, day=0, redeem=False): #免費領取
	header['Referer'] = "https://dailylogin.lol.garena.tw/?token={}".format(token)
	res = requests.get("https://dailylogin.lol.garena.tw/api/info?token={}".format(token), headers=header)	
	header["x-csrftoken"] = dict(res.cookies)['csrftoken']
	url = "https://dailylogin.lol.garena.tw/api/receive" if not redeem else "https://dailylogin.lol.garena.tw/api/redeem"
	data = {'day': day}
	res = requests.post(url, headers=header, data=json.dumps(data), cookies=res.cookies)
	if res.status_code==200:
		resJson = json.loads(res.text)
		if 'actual_name' in resJson.keys():
			printLog("  已兌換獎勵：{}".format(resJson['actual_name']))
			time.sleep(0.25)
		elif 'error' in resJson.keys():
			if resJson['error'] != 'COMMON': printLog(resJson['error'])
		return resJson
def supplement(token): #補簽
	header['Referer'] = "https://dailylogin.lol.garena.tw/?token={}".format(token)
	res = requests.get("https://dailylogin.lol.garena.tw/api/info?token={}".format(token), headers=header)
	header["x-csrftoken"] = dict(res.cookies)['csrftoken']
	url = "https://dailylogin.lol.garena.tw/api/supplement"
	res = requests.post(url, headers=header, cookies=res.cookies)
	if res.status_code==200:
		resJson = json.loads(res.text)
		if 'supplemented_date' in resJson.keys():
			timestamp = resJson['supplemented_date']
			timeString = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
			printLog("  已補簽到：{}".format(timeString))
		else:
			return False
def couponqueen(token):
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
def main():
	parser = getParser()
	args = parser.parse_args()

	if os.path.exists("token.txt"):
		with open("token.txt" , "r", encoding = 'utf-8-sig') as data:
			tokenDict = {line.strip().split("\t")[0]:line.strip().split("\t")[1] for line in data }
	else: tokenDict = {}

	tokens = getToken(args.dir, multi=True, sucPrint=False)
	while(not tokens):
		path = input("請輸入LeagueClient Logs之路徑：\n ")
		tokens = getToken(path, multi=True)

	tokenDict = loadDict(filename="token.txt")
	for token in tokens:
		if token not in tokenDict.keys():
			tokenDict[token] = 0

	for token in tokenDict.keys():
		countDay = 31 * (time.localtime().tm_mon -1) + time.localtime().tm_mday
		if tokenDict[token] > countDay-26 or tokenDict[token] >= 14:
			continue
		info = getInfo(token)
		if "logined" not in info.keys(): 
			if info["error"] == 'LOGIN_FAILED': #LOGIN_FAILED
				tokenDict[token] = 99
				continue
			else:
				print(info)
		print(token)
		#couponqueen(token)
		for day in range(int(tokenDict[token]), min(countDay-25, 14)):
			if info['login_rewards'][day]['received_date']:
				tokenDict[token] = day+1
				continue
			if info["logined"][day]:
				receive(token, day=day)
				tokenDict[token] = day+1
			elif len(info["supplemented_dates"]) < 4: #補簽到
				supplement(token)
				receive(token, day=day)
				info = getInfo(token)
			if day==1: receive(token, day=1, redeem=True)
			if day==12: receive(token, day=12, redeem=True)
		receive(token, day=1, redeem=True)
		receive(token, day=12, redeem=True)

	saveDict(tokenDict, filename="token.txt", saveNum=88)
if __name__ == '__main__':
	#getLog(["虎年賀新春限定禮包", "四個新春狂歡造型碎片"], filename="lcu.log")
	#exit()

	parser = getParser()
	args = parser.parse_args()

	#main()

	token = getToken(args.dir, multi=False, sucPrint=False)
	errDic = getErrDic()
	couponqueen(token)

	import lcu
	lcu.main()

	#auth = lcu.getAuth("C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
	#print(lcu.getProfile(auth,"神才就狂"))