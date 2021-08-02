import os, time, random
import requests, json
import winsound
import pyautogui
import keyboard
import pyperclip

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
	news = ["32165"] #"32164","32159", "32153"
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
def checkKeyEnd():
	if keyboard.is_pressed('esc'):
		print("Ended by User. Good Bye~")
		exit()
def checkKeyGetPoint():
	if keyboard.is_pressed('q'):
		winsound.Beep(100, 800)
		return pyautogui.position()
	return False
def checkKeyPause():
	if keyboard.is_pressed('p'):
		os.system("pause")
def getPosSubmit():
	posSubmit = None
	while not posSubmit:
		print("正在尋找兌換鍵位置")
		posSubmit1 = pyautogui.locateCenterOnScreen('./imgs/submit1.png', confidence=0.8)
		posSubmit2 = pyautogui.locateCenterOnScreen('./imgs/submit2.png', confidence=0.8)
		posSubmit = posSubmit1 if posSubmit1 else (posSubmit2 if posSubmit2 else None)
		if keyboard.is_pressed('q'): #手動指定位置
			posSubmit = pyautogui.position()
		checkKeyEnd()
	print("已獲取兌換鍵位置: {}".format(posSubmit))
	return posSubmit
def getposInbox():
	posInbox = None
	while not posInbox:
		print("正在尋找輸入框位置")
		posInbox1 = pyautogui.locateCenterOnScreen('./imgs/inbox1.png', confidence=0.8)
		posInbox2 = pyautogui.locateOnScreen('./imgs/inbox2.png', confidence=0.8)
		if posInbox2:
			posInbox2 = pyautogui.center(posInbox2) + (0,posInbox2.width/2)
		posInbox = posInbox1 if posInbox1 else (posInbox2 if posInbox2 else None)
		if keyboard.is_pressed('q'): #手動指定位置
			posInbox = pyautogui.position()
		checkKeyEnd()
	print("已獲取輸入框位置: {}".format(posInbox))
	return posInbox
def getPosConfirm():
	posConfirm,PosCancel = None, None
	while not posInbox:
		print("正在尋找確認鍵位置")
		checkKeyGetPoint()
		posInbox1 = pyautogui.locateCenterOnScreen('./imgs/inbox1.png', confidence=0.8)
		posInbox2 = pyautogui.locateOnScreen('./imgs/inbox2.png', confidence=0.8)
		if posInbox2:
			posInbox2 = pyautogui.center(posInbox2) + (0,posInbox2.width/2)
			#pyautogui.moveTo(posInbox2, duration=1)
		posInbox = posInbox1 if posInbox1 else (posInbox2 if posInbox2 else None)
		checkKeyEnd()
	print("已獲取輸入框位置: {}".format(posInbox))
	return posInbox
def confirmObject(errPrint=True,errNum=5):
	for i in range(2):
		posConfirm = None
		errSubmit = 0
		while posConfirm is None and errSubmit < errNum:
			checkKeyEnd()
			posConfirm = pyautogui.locateCenterOnScreen('imgs/confirm.png', confidence=0.8)
			errSubmit += 1
			time.sleep(0.15)
		if errSubmit >= errNum and errPrint:
			print("出現異常，無法跳出確認視窗")
			break
		pyautogui.click(posConfirm)
		time.sleep(0.2)
		
def balloonExchange():
	posExArea = pyautogui.locateCenterOnScreen('./imgs/exArea.png') #Exchange Area
	if posExArea:
		pyautogui.click(posExArea)
		time.sleep(0.5)
		scroll = 0
		posExchange = pyautogui.locateCenterOnScreen('./imgs/exchange1.png', confidence=0.8)
		while(posExchange or scroll <= 2):
			posExchange = pyautogui.locateCenterOnScreen('./imgs/exchange1.png', confidence=0.8)
			if posExchange:
				pyautogui.click(posExchange)
				confirmObject(errNum=12)
				time.sleep(0.2)
			else:
				confirmObject(errPrint=False, errNum=3)
				posExchange2 = pyautogui.locateCenterOnScreen('./imgs/exchange2.png', confidence=0.8)
				pyautogui.moveTo(posExchange2,duration=0.2)
				pyautogui.scroll(-500)
				scroll += 1 
		posClose = pyautogui.locateCenterOnScreen('./imgs/close.png', confidence=0.8)
		if posClose: pyautogui.click(posClose)
def checkFinish():
	posFinish = pyautogui.locateCenterOnScreen('./imgs/finish.png') #60/60
	if posFinish:
		balloonExchange()
		winsound.Beep(1000, 300)
		input("已兌換60顆氣球完畢，請按Enter離開程式") #待加上重新開始
		exit()

print("注意事項：\n - 請確認視窗沒有擋住序號輸入框和兌換區的按鈕後再開始執行\n - 若無法正常點擊請嘗試以管理員身分執行")
input("(Press \"Enter\" to start, \"Esc\" to stop, \"p\" to pause.)")
posSubmit = getPosSubmit()
posInbox = getposInbox()
count = 1
errCode = 0

while(True and errCode < 3):
	for index, code in enumerate(parseCode(getGarenaComment(num=1)), start=1):
		checkKeyEnd()
		checkFinish()
		
		pyperclip.copy(code)
		print("正在輸入第{:^3d}組序號：{}".format(count,code))
		#print(f'正在輸入第{count}個序號, {code}')
		pyautogui.click(posInbox)
		pyautogui.hotkey('ctrl', 'a')
		pyautogui.press('delete')
		#pyautogui.write(code)
		pyautogui.hotkey('ctrl', 'v')
		pyautogui.click(posSubmit)
		confirmObject(errNum = 5)
		count = count +1
		time.sleep(0.1)
		if keyboard.is_pressed('p'): #Paused
			os.system("pause")
			posSubmit = getPosSubmit()
			posInbox = getposInbox()
		