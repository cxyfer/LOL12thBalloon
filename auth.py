import os, re

folder = "C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs"

def getAuth(folder, sucPrint=True, errPrint=True):
	if os.path.isdir(folder):
		for file in sorted(os.listdir(folder),reverse=True):
			reLog = re.match(r'.+?_LeagueClientUx\.log', file)
			if reLog:
				try:
					with open("{}\\{}".format(folder,file), 'r', encoding="utf-8") as data:
						reAuth = re.search(r'(https://riot:.+?@127\.0\.0\.1:\d+?)/(index|bootstrap)\.html\"', data.read())
				except:
					with open("{}\\{}".format(folder,file), 'r') as data:
						reAuth = re.search(r'(https://riot:.+?@127\.0\.0\.1:\d+?)/(index|bootstrap)\.html\"', data.read())
				if reAuth:
					auth = reAuth.group(1).strip()
					print("已獲取AuthInfo：{}\n".format(auth)) if sucPrint else print(end="")
					return auth
		if len(authList) > 0 : return authList
	print("錯誤：無法從LOL安裝路徑獲取授權資訊，請嘗試輸入安裝路徑。") if errPrint else print(end="")
	return False
def getAuth2(sucPrint=True, errPrint=True):
	cmd = "wmic PROCESS WHERE name='LeagueClientUx.exe' GET commandline"
	process = os.popen(cmd)
	res = process.read()
	process.close()
	reAuth = re.search(r'\"--remoting-auth-token=(.+?)\".+\"--app-port=(\d+)\"', str(res))
	if reAuth:
		auth = f"https://riot:{reAuth.group(1)}@127.0.0.1:{reAuth.group(2)}"
		print("已獲取AuthInfo：{}\n".format(auth)) if sucPrint else print(end="")
		return auth
	return False
	
def getToken(folder="C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs", sucPrint=True, errPrint=True, multi=False):
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

if __name__ == '__main__':
	#token = getToken("C:\\Garena\\Games\\32775\\Game\\Logs\\LeagueClient Logs", sucPrint=False)
	#print(token)
	getAuth2()