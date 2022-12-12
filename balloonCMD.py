import os, re, time
import random
import requests, json
import argparse

requests.packages.urllib3.disable_warnings()
def getToken(folder,errPrint=True):
	if os.path.isdir(folder):
		for file in sorted(os.listdir(folder),reverse=True):
			reLog = re.match(r'.+?_LeagueClientUx\.log', file)
			if reLog:
				try:
					with open("{}\\{}".format(folder,file), 'r', encoding="utf-8") as data:
						reToken = re.search(r'https://.+?\.lol\.garena\.tw/.+?token=(.+)\"', data.read())
				except:
					with open("{}\\{}".format(folder,file), 'r') as data:
						reToken = re.search(r'https://.+?\.lol\.garena\.tw/.+?token=(.+)\"', data.read())
				if reToken:
					token = reToken.group(1)
					print("已從LOL安裝路徑獲取token：{}".format(reToken.group(1)))
					return reToken.group(1)
	print("錯誤：無法從LOL安裝路徑獲取token，請嘗試輸入安裝路徑或手動獲取token。") if errPrint else print(end="")
	return False

def parseCode(inputList):
	codeList = []
	for line in inputList:
		findPos = re.search(r'LOL[A-Za-z0-9]{10}', line)
		if findPos:
			code = findPos.group(0)
			codeList.append(code)
	return codeList if len(codeList) > 0 else False
def getGarenaComment(rootID=0,num=5):
	url = "https://commenttw.garenanow.com/api/comments/get/"
	header = {'User-Agent': 'Garenagxx/2.0.1909.2618 (Intel x86_64; zh-Hant; TW)',"Content-Type": 'application/json'}
	news = ["32194","32193"] #"32165", "32164", "32159", "32153"
	data = {"obj_id": "tw_32775_newnews_{}".format(random.choice(news)),
			"root_id": 0,
			"size": num, #留言數量
			"replies": 10, 
			"order": 2,
			"replies_order": 2,
			"session_key":"cda0c8df05ba75fa8edd72b49eac81ee5263f83c4c8214efdeca7a42800c15fa",
			"web_app_id": 10047
			}
	res = requests.post(url, headers=header, data=json.dumps(data), verify=False)
	if res.status_code == 200 :
		resJson = json.loads(res.text)
		contentList = [comment['extra_data']['content'].strip() for comment in resJson["comment_list"]]
		codeList = parseCode(contentList)
		return codeList if codeList else getGarenaComment(num=num)
def getBahamutComment(num=5):
	url = "https://forum.gamer.com.tw/ajax/moreCommend.php?bsn=17532&snB=5838400&returnHtml=0"
	header = {	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
				"content-type": "application/json; charset=utf-8" }
	res = requests.post(url, headers=header)
	if res.status_code == 200 :
		resJson = json.loads(res.text)
		contentList = [resJson[str(i)]['comment'].strip() for i in range(num)]
		codeList = parseCode(contentList)
		return codeList if codeList else getBahamutComment(num=num)
def codeSubmit(header,code):
	url = "https://bargain.lol.garena.tw/api/enter"
	header = {	"User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/11.15.388.2387 (CEF 74) Safari/537.36",
				"Content-Type": 'application/json',
				"Accept-Encoding": "gzip,deflate",
				"Referer": "https://bargain.lol.garena.tw/?token={}".format(token),
				"token":token
			}
	data = {'code':code, 'confirm':False}
	res = requests.post(url, headers=header, json=data)
	data['confirm'] = True
	res = requests.post(url, headers=header, json=data)
	resJson = json.loads(res.text)
	return resJson
errDic = {
		"ERROR__SERVER_ERROR": "系統忙碌中，請稍後再試！",
		"ERROR__BAD_REQUEST": "系統錯誤，請稍後再試！",
		"ERROR__UNDER_MAINTENANCE": "系統維護中",
		"ERROR__ENTER_CODE_AMOUNT_OUT_OF_QUOTA": "您輸入邀請碼的數量已經達到上限囉",
		"ERROR__CODE_ALREADY_REDEEMED": "已經輸入過這個序號囉",
		"ERROR__INVALID_CODE": "序號錯誤",
		"ERROR__OWNED_CODE": "不能輸入自己的邀請碼喔",
		"ERROR__INVITATION_AMOUNT_NOT_ENOUGH": "對方的邀請名額不足",
		"ERROR__CODE_EXPIRED": "序號過期了",
		"ERROR__TOO_MANY_REQUESTS": "手速太快了，請再試一次",
		"ERROR__CODE_OUT_OF_QUOTA": "序號已經被兌換完畢了",
		"ERROR__INVITER_PROGRESS_FULL": "對方尚未開啟新的一輪集 Fun",
		"ERROR__BANNED_PLAYER": "玩家已被禁止進入活動",
		"ERROR__TOKEN_REWARD_OUT_OF_QUOTA": "已經領完獎勵囉",
		"ERROR__GAME_LOGIN_FAILED": "登入失敗",
		"ERROR__ANNIVERSARY_REWARD_ALREADY_REDEEMED": "已兌換登入造型二十選一",
	}
def getBalloon(token,sucDelay=1.25,errDelay=0.5):
	countSubmit = countSuccess = errCode = allAmount = 0
	time1 = time.time()
	print("當前設定：輸入失敗後延遲{}秒、輸入成功後延遲{}秒".format(errDelay,sucDelay))
	while(errCode < 3 and allAmount < 60):
		for code in parseCode(getGarenaComment(num=args.num) if args.site.lower() == "garena" else getBahamutComment(num=args.num)):
			countSubmit += 1
			print("  正在輸入第{:^3d}組序號 {} : ".format(countSubmit,code),end="")
			res = codeSubmit(token,code)
			if "error" in res.keys():
				if res['error'] == "ERROR__ENTER_CODE_AMOUNT_OUT_OF_QUOTA" or allAmount == 60:
					time2 = time.time()
					print("\n已獲取{}/60顆氣球，共嘗試{}次、費時{}秒，準備開始自動兌換獎勵。".format(countSuccess,countSubmit,round(time2-time1,2)))
					time.sleep(1)
					return True
				print("錯誤！{}".format(errDic[res['error']]))
				time.sleep(errDelay)
			else:
				allAmount = res["enter_code_amount"]
				curAmount = res["current_token_amount"]
				print("成功！已兌換{}顆氣球，當前擁有{}顆氣球".format(allAmount,curAmount))
				countSuccess +=1
				time.sleep(sucDelay)
def redeemBalloon(token,item_id,typ=2):
	url = "https://bargain.lol.garena.tw/api/redeem"
	header = {	"User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/11.15.388.2387 (CEF 74) Safari/537.36",
				"Content-Type": 'application/json',
				"Referer": "https://bargain.lol.garena.tw/?token={}".format(token),
				"token":token
			}
	data = {'item_id':item_id, 'type':typ}
	res = requests.post(url, headers=header, data=json.dumps(data))
	resJson = json.loads(res.text)
	if 'reward' in resJson.keys():
		print("  已兌換獎勵：{}".format(resJson['reward']['name']))
		time.sleep(1)
def Balloon(token):
	for i in range(1,10):
		redeemBalloon(token,i)
	redeemBalloon(token,9)
	'''
	if(getBalloon(token,sucDelay=args.sucDelay,errDelay=args.errDelay)):
		for i in range(1,10):
			redeemBalloon(token,i)
		redeemBalloon(token,9)
	'''
	if args.skin : redeemBalloon(token, args.skin, typ=1)
	#input("已兌換完畢，請按Enter離開程式")

def getParser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dir", "--folder", default="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs")
	parser.add_argument("-t", "--token",  default="")
	parser.add_argument("-f", "--site", "--from", default="Garena")
	parser.add_argument("-n", "--num", default="5", type=int)
	parser.add_argument("-s", "--sucDelay", default="1.25", type=float)
	parser.add_argument("-e", "--errDelay", default="0.5", type=float)
	parser.add_argument("-i", "--skin", "--item", default="0", type=int)
	return parser

if __name__ == '__main__':
	global args
	parser = getParser()
	args = parser.parse_args()
	token = args.token if len(args.token)==64 else getToken(args.dir)
	while(not token):
		url = input("請輸入token，或貼上包含token的網址、或輸入LeagueClient Logs之路徑：\n ")
		reUrl = re.match(r'https://.+?\.lol\.garena\.tw/.+?token=(.+)', url)
		token = reUrl.group(1) if reUrl else (url if len(url) == 64 else getToken(url))
	if token: Balloon(token)