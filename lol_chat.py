import os, time
import requests, json

def printJSON(data):
	print(json.dumps(data, ensure_ascii=False, indent=4))

def getProfile(auth, name):
	url = auth + "/lol-summoner/v2/summoners/names"
	res = requests.post(url, verify=False, data=json.dumps([name])).json()
	return res[0] if res else False
def loadFriendList(filename="friends.txt"):
	if os.path.exists(filename):
		with open(filename , "r", encoding = 'utf-8-sig') as data:
			friendList = [ line.strip() for line in data if line.strip() and not line.startswith("#")]
	else: friendList = []
	return friendList
def addFriendsByList(auth, friendList, note="LCU", groupName=False):
	url = f"{auth}/lol-chat/v1/friends"
	res = requests.get(url, verify=False).json()
	myFriends = {friend['name']:friend for friend in res}
	url = f"{auth}/lol-chat/v1/friend-requests"
	reqs = requests.get(url, verify=False).json()
	myRequests = [req['name'] for req in reqs]
	
	if len(reqs) >= 50: return False
	if groupName:
		groupId = addFriendGroup(auth, groupName=groupName)

	errNum = 0
	for friend in friendList:
		if friend not in myFriends.keys():
			if friend not in myRequests:
				res = sendFriendRequests(auth, friend, note=note)
				errNum += (1 if res == 500 else 0)
				time.sleep(0.2)
		elif groupName:
			if myFriends[friend]['groupName'] != groupName:
				addFriendToGroup(auth, friend, groupId)
				time.sleep(0.1)
		if errNum>5: break
	if errNum>5:
		print(f"  失敗次數過多，等待10秒後重試")
		time.sleep(10)
		return addFriendsByList(auth, friendList, note=note, groupName=groupName)

def sendFriendRequests(auth, name, note="LCU"):
	url = auth + "/lol-chat/v1/friend-requests"
	profile = getProfile(auth, name)
	if not profile: return False
	data = {"direction": "out", "name": name, "note": note, "summonerId": profile['summonerId']}
	res = requests.post(url, verify=False, data=json.dumps(data))
	if res.status_code == 204 :
		print("  已送出對 {} 的交友邀請".format(name))
	elif res.status_code == 500 :
		print("  無法送出對 {} 的交友邀請，可能是我方或對方待處理已滿".format(name))
	return res.status_code
def addFriendGroup(auth, groupName='newGroup'):
	url = auth + "/lol-chat/v1/friend-groups"
	res = requests.get(url, verify=False).json()
	myGroups = {group['name']:group['id'] for group in res}
	if groupName not in myGroups:
		res = requests.post(url, verify=False, data=json.dumps({'name': groupName}))
		if res.status_code == 204 :
			print("  已創建好友群組：{}".format(groupName))
		res = requests.get(url, verify=False).json()
	return max([group['id'] if group['name']==groupName else -1 for group in res])
def addFriendToGroup(auth, name, groupId):
	profile = getProfile(auth, name)
	if not profile: return False
	url = f"{auth}/lol-chat/v1/friends/{profile['puuid']}@pvp.net"
	res = requests.put(url, verify=False, data=json.dumps({"groupId": groupId}))
	return True if res.status_code == 201 else False
def addFriendToGroupByList(auth, friendList, groupName="LCU", groupId=0):
	url = f"{auth}/lol-chat/v1/friends"
	res = requests.get(url, verify=False).json()
	myFriends = {friend['name']:friend for friend in res}
	groupId = addFriendGroup(auth, groupName=groupName) if not groupId else groupId
	for friend in friendList:
		if friend in myFriends.keys():
			if myFriends[friend]['groupId'] != groupId:
				addFriendToGroup(auth, friend, groupId)
def deleteFriendsByList(auth, deleteList):
	url = f"{auth}/lol-chat/v1/friends"
	res = requests.get(url, verify=False).json()
	for friend in res:
		if friend['name'] in deleteList:
			deleteFriend(auth, friend['name'], pid=friend['pid'])
			time.sleep(0.1)
	url = auth + "/lol-chat/v1/friend-requests"
	reqs = requests.get(url, verify=False).json()
	for req in reqs:
		if req['name'] in deleteList:
			deleteFriendRequests(auth, req['name'])
			time.sleep(0.1)
def deleteFriendsByNote(auth, note="LCU"):
	url = f"{auth}/lol-chat/v1/friends"
	res = requests.get(url, verify=False).json()
	for friend in res:
		if friend['note'] == note:
			deleteFriend(auth, friend['name'], friend['pid'])
			time.sleep(0.1)
def deleteAllFriends(auth):
	url = f"{auth}/lol-chat/v1/friends"
	res = requests.get(url, verify=False).json()
	for friend in res:
		deleteFriend(auth, friend['name'], friend['pid'])
		time.sleep(0.1)
def deleteFriend(auth, name, pid=""):
	if not pid:
		profile = getProfile(auth, name,)
		if not profile: return False
		url = f"{auth}/lol-chat/v1/friends/{profile['puuid']}@pvp.net"
	else:
		url = f"{auth}/lol-chat/v1/friends/{pid}"
	res = requests.delete(url, verify=False)
	if res.status_code == 204 :
		print("  已刪除好友：{}".format(name))
def deleteFriendRequests(auth, name, pid=""):
	if not pid:
		profile = getProfile(auth, name)
		if not profile: return False
		url = f"{auth}/lol-chat/v1/friend-requests/{profile['puuid']}@pvp.net"
	else:
		url = f"{auth}/lol-chat/v1/friend-requests/{pid}"
	res = requests.delete(url, verify=False)
	if res.status_code == 204 :
		print("  已刪除對 {} 的交友邀請".format(name))
def cleanAllFriendRequests(auth, direction=""):
	url = auth + "/lol-chat/v1/friend-requests"
	reqs = requests.get(url, verify=False).json()
	for req in reqs:
		url = f"{auth}/lol-chat/v1/friend-requests/{req['id']}"
		res = requests.delete(url, verify=False)
		if res.status_code == 204 :
			print("  已刪除對 {} 的交友邀請".format(req['name']))
def accessAllFriendRequests(auth):
	url = auth + "/lol-chat/v1/friend-requests"
	reqs = requests.get(url, verify=False).json()
	errNum = 0
	for req in reqs:
		if req["direction"] == "in":
			req["direction"] == "out"
			res = requests.post(url, verify=False, data=json.dumps(req))
			if res.status_code == 204 :
				print("  已接受 {} 的交友邀請".format(req["name"]))
			else:
				print("  無法接受 {} 的交友邀請".format(req["name"]))
				errNum += 1
			time.sleep(0.2)
			if errNum>5: break
	if errNum>5:
		print(  f"失敗次數過多，等待10秒後重試")
		time.sleep(10)
		return accessAllFriendRequests(auth)
