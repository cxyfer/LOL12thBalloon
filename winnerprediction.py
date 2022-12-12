import os, re, time
import requests, json
import random
import argparse

requests.packages.urllib3.disable_warnings()
UA = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/12.18.469.7517 (CEF 74) Safari/537.36"

errDic = {
		'ERROR__SERVER_ERROR': '伺服器錯誤，請稍後再試',
		'ERROR__BAD_REQUEST': '參數錯誤',
		'ERROR__LEVEL_NOT_ENOUGH': '未達參與活動的等級，請先將召喚師等級提升至 10 等再重新進入活動。',
		'ERROR__UNDER_MAINTENANCE': '活動維護中，請稍後再試',
		'ERROR__PREDICTION_LOCKED': '預測已鎖定，不能修改內容',
		'ERROR__NOT_EVENT_PERIOD': '目前不是活動時間',
		'ERROR__GOP_LOGIN_FAILED': 'GOP登入失敗',
		'ERROR__HERO_NOT_OWNED': '你尚未擁有這隻英雄。',
		'ERROR__SERVER_BUSY': '伺服器忙碌中請稍後再試',
		'ERROR__FORBIDDEN': 'forbidden IP',
		'ERROR__GAME_LOGIN_FAILED': 'GAME登入失敗',
		'ERROR__ALREADY_REDEEMED': '已經領取過獎勵囉',
	}
def printLog(text, end="\n"):
	print(text, end=end)
	with open("login.log","a", encoding = 'utf8') as data:
		data.write(str(text)+end)
def printJSON(data):
	print(json.dumps(data, ensure_ascii=False, indent=4))
def printMask(text, k=5):
	text, n = re.subn('|'.join(random.choices(text, k=k)), '#', text)
	if (n<len(text)/4):
		return printMask(text, k=k+1)
	print(text)
def getErrDic():
	url = "https://rosetta-tw.garenanow.com/transify/2807?lang=2"
	header = {"Referer": "https://winnerprediction.lol.garena.tw"}
	res = requests.get(url, headers=header)
	res.encoding = 'utf8'
	resJson = json.loads(res.text)
	return {info if info.startswith("ERROR") else "" :resJson[info]  for info in resJson.keys()}
def loadpredictDict(filename="code.txt"):
	if os.path.exists(filename):
		with open(filename , "r", encoding = 'utf-8-sig') as data:
			predictDict = {line.strip().split("\t")[0]:int(line.strip().split("\t")[1]) for line in data }
	else: predictDict = {}
	return predictDict
def savepredictDict(predictDict, filename="code.txt", saveNum=5):
	with open(filename, "w", encoding = 'utf-8-sig') as data:
		for key in predictDict.keys():
			if int(predictDict[key]) < saveNum :
				data.write("{}\t{}\n".format(key, predictDict[key]))
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
def getProfile(token, retry=3):
	url = "https://winnerprediction.lol.garena.tw/api/profile"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://winnerprediction.lol.garena.tw/?token={}".format(token),
				"token": token,
			}
	try:
		res = requests.get(url, headers=header).json()
	except:
		return getProfile(token, retry=retry-1) if (retry>0) else False
	if ('error' in res):
		print(errDic[res['error']])
	return res if ('error' not in res) else False
def getConfig(token, retry=3):
	url = "https://winnerprediction.lol.garena.tw/api/config"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://winnerprediction.lol.garena.tw/?token={}".format(token),
				"token": token,
			}
	try:
		res = requests.get(url, headers=header).json()
	except:
		return getConfig(token, retry=retry-1) if (retry>0) else False
	if ('error' in res):
		print(res['error'])
	return res if ('error' not in res) else False
def loadPredict(filename="winnerprediction.txt"):
	if os.path.exists(filename):
		with open(filename , "r", encoding = 'utf-8-sig') as data:
			predictDict = {int(line.strip().split(":")[0]) : int(line.strip().split(":")[1]) if line.strip().split(":")[1]!='' else 0 for line in data }
		return predictDict
	else:
		print("預測檔案不存在！")
		exit()
def predict(token, debug=False):
	url = "https://winnerprediction.lol.garena.tw/api/predict"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://winnerprediction.lol.garena.tw/?token={}".format(token),
				"token": token,
			}
	profile = getProfile(token)
	config = getConfig(token)
	configDict = {game['game_id']:game for stage in config['stage'] for match_date in stage['match_date'] for game in match_date['game'] }
	gameDict = {game['game_id']:game['prediction'] for stage in profile['stage'] for match_date in stage['match_date'] for game in match_date['game'] }
	success = []
	for game_id in predictDict.keys():
		if predictDict[game_id] == gameDict[game_id] or (not predictDict[game_id]) and gameDict[game_id]:
			success.append(str(game_id))
			continue
		data = {'game_id': game_id, 'prediction':predictDict[game_id] if predictDict[game_id]>0 else random.randint(1,2)}
		try:
			res = requests.post(url, headers=header, json=data).json()
		except:
			time.sleep(0.2)
			try:
				res = requests.post(url, headers=header, json=data).json()
			except:
				time.sleep(0.2)
				continue
		if 'success' in res.keys():
			success.append(str(game_id))
		elif debug:
			if res['error'] in errDic: print(errDic[res['error']])
			else: print(res['error'])
	print("  預測 {} 場比賽成功，比賽ID為：{}".format(len(success), ",".join(success)))
	return len(success)

def redeem(token, debug=False):
	url = "https://winnerprediction.lol.garena.tw/api/redeem"
	header = {	"User-Agent": UA,
				"Content-Type": 'application/json',
				"Referer": "https://winnerprediction.lol.garena.tw/",
				"token": token,
			}
	profile = getProfile(token)
	config = getConfig(token)
	successList, rewardList = [], []

	for stage in profile['stage']:
		for match_date in stage['match_date']:
			amount = match_date['success_prediction_amount']
			if amount > 0 and match_date['redeem_status'] == 1: #0：未結束、1：尚未兌換、2：已兌換
				has_boost = True if match_date['current_victory_amount'] > 0 else False
				match_date_id = match_date['match_date_id']
				indexStage = profile['stage'].index(stage)
				indexMatchDate = stage['match_date'].index(match_date)
				rewards = config['stage'][indexStage]['match_date'][indexMatchDate]['reward']
				reward_id = rewards[amount-1]['reward_id']

				data = {'type':1, 'has_boost': has_boost, 'match_date_id':match_date_id, 'reward_id':[reward_id]}
				try:
						res = requests.post(url, headers=header, data=json.dumps(data)).json()
				except:
					continue

				if 'success' in res.keys():
					successList.append(str(match_date_id))
					rewardList.append(rewards[amount-1]['reward_name'])
				elif debug:
					if res['error'] in errDic: print(errDic[res['error']])
					else: print(res['error'])
	if len(successList) > 0:
		print("  兌換第 {} 天獎勵成功，獎勵為：{}".format(", ".join(successList), "、".join(rewardList)))

	for milestone in profile['milestone_reward']:
		if profile['total_success_prediction_amount'] >= milestone['success_prediction_amount'] and not milestone['redeemed']:
			data = {'type':2, 'reward_id':[milestone['reward_id']]}
			try:
				res = requests.post(url, headers=header, data=json.dumps(data)).json()
				if 'success' in res.keys():
					print("  已兌換 {}勝 獎勵：{}".format(milestone['success_prediction_amount'], milestone['reward_name']))
			except:
				continue
	return

def getParser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", "--folder", default="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
	parser.add_argument("-t", "--token",  default="")
	return parser

def main():
	global args, predictDict
	parser = getParser()
	args = parser.parse_args()

	tokens = getToken(args.dir, multi=True, sucPrint=False)
	while(not tokens):
		path = input("請輸入LeagueClient Logs之路徑：\n ")
		tokens = getToken(path, multi=True)
	tokenpredictDict = loadpredictDict(filename="token.txt")
	for token in tokens:
		if token not in tokenpredictDict: tokenpredictDict[token] = 0

	predictDict = loadPredict()
	for token in tokenpredictDict:
		if tokenpredictDict[token] == len(predictDict): continue
		profile = getProfile(token)
		#printJSON(profile)
		if not profile:
			tokenpredictDict[token] = 999
			continue
		print(token)
		#printMask(token)
		tokenpredictDict[token] = predict(token, debug=True)
		tokenpredictDict[token] = tokenpredictDict[token] if tokenpredictDict[token] else 9999
		redeem(token)

	savepredictDict(tokenpredictDict, filename="token.txt", saveNum=800)

if __name__ == '__main__':

	main()