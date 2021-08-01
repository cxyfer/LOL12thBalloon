import os, re, time
import requests, json

requests.packages.urllib3.disable_warnings()
def parseCode(inputList):
	codeList = []
	for line in inputList:
		findPos = line.find("LOL")
		if findPos != -1:
			code = line[findPos:findPos+13]
			codeList.append(code)
	return codeList if len(codeList) > 0 else False
def getGarenaComment(rootID=0,num=5):
	url = "https://commenttw.garenanow.com/api/comments/get/"
	header = {'User-Agent': 'Garenagxx/2.0.1909.2618 (Intel x86_64; zh-Hant; TW)',"Content-Type": 'application/json'}
	data = {"obj_id": "tw_32775_newnews_32159",
			#"obj_id": "tw_32775_newnews_32153",
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
		"ERROR__GAME_LOGIN_FAILED": "登入失敗"
	}
def codeSubmit(token,code):
	url = "https://bargain.lol.garena.tw/api/enter"
	header = {	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
				"Content-Type": 'application/json',
				#"X-CSRFToken": "FFbSAmMWmZUC1i0WZukgnEKzKP3bsjgjR60ZFIFZcpgnnpIPOGt4R4vTdY6jzHg3",
				"token":token
			}
	data = {'code':code, 'confirm':True}
	res = requests.post(url, headers=header, data=json.dumps(data))
	resJson = json.loads(res.text)
	return resJson
	if "error" in resJson.keys():
		print(errDic[resJson['error']])
	else:
		print(resJson)
def getBalloon(token):
	countSubmit = countSuccess = errCode = finish = 0
	time1 = time.time()
	while(not finish and errCode < 3):
		for index, code in enumerate(parseCode(getGarenaComment(num=3)), start=1):
			print("正在輸入第{:^3d}組序號 {} ：".format(countSubmit,code),end="")
			res = codeSubmit(token,code)
			if "error" in res.keys():
				if res['error'] == "ERROR__ENTER_CODE_AMOUNT_OUT_OF_QUOTA":
					time2 = time.time()
					print("已獲取{}/60顆氣球，共兌換{}次、費時{}秒，準備開始自動兌換獎勵。".format(countSuccess,countSubmit,round(time2-time1,2)))
					time.sleep(0.5)
					return True
				print("錯誤！{}".format(errDic[res['error']]))
				time.sleep(0.1)
			else:
				allAmount = res["enter_code_amount"]
				curAmount = res["current_token_amount"]
				print("成功！已兌換{}顆氣球，當前擁有{}顆氣球".format(allAmount,curAmount))
				countSuccess +=1
				time.sleep(0.4)
			countSubmit += 1
def redeemBalloon(token,item_id):
	url = "https://bargain.lol.garena.tw/api/redeem"
	header = {	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
				"Content-Type": 'application/json',
				"token":token
			}
	data = {'item_id':item_id, 'type':2}
	res = requests.post(url, headers=header, data=json.dumps(data))
	resJson = json.loads(res.text)
	if 'reward' in resJson.keys():
		print("已兌換獎勵：{}".format(resJson['reward']['name']))
	#else:
	#	print(resJson)
def Balloon(token):
	if(getBalloon(token)):
		for i in range(1,10):
			redeemBalloon(token,i)
		redeemBalloon(token,9)
	input("已兌換完畢，請按Enter離開程式")

if __name__ == '__main__':
	token = ""
	while(not token):
		url = input("請輸入token，或貼上活動頁面「個人數據回顧」中包含token的網址：")
		reUrl = re.match(r'https://datareview\.lol\.garena\.tw/.+?token=(.+)', url)
		token = reUrl.group(1) if reUrl else (url if len(url) == 64 else token)
		if token: Balloon(token)

