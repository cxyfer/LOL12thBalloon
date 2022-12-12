#!/usr/bin/python
import sqlite3 ,re

def init(db_name,table_name):
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()
	execute = '''CREATE TABLE IF NOT EXISTS %s
		(更新 VARCHAR(16),
		ACID INT PRIMARY KEY NOT NULL,
		name VARCHAR(16) NOT NULL,
		LV INT NOT NULL,
		RP INT NOT NULL,
		ownBE INT NOT NULL,
		allBE INT NOT NULL,
		ownOE INT NOT NULL,
		allOE INT NOT NULL,
		英雄數 INT NOT NULL,
		造型數 INT NOT NULL,
		英雄 TEXT NOT NULL,
		英雄略 TEXT NOT NULL,
		造型 TEXT NOT NULL,
		英雄碎片 TEXT NOT NULL,
		造型碎片 TEXT NOT NULL,
		INFO1 TEXT,
		INFO2 TEXT,
		UNIQUE(ACID)
		)''' % (table_name)
	cursor.execute(execute)
	cursor.close()
	conn.close()

def build_tsv(tsvname): #將之前的TSV格式資料匯入成List並做改寫成新格式
	with open(tsvname , "r", encoding = 'utf-8-sig') as data:
		List = []
		for line in data:
			part1 = line.strip().split("\t")[0:4]
			part2 = line.strip().split("\t")[4:10]
			part3 = line.strip().split("\t")[10]
			if re.search(r"\((db_\d+)\)",line): #如果能從資料夾名稱找到dbID
				MainID = re.search(r"\((db_\d+)\)",line).group(1)
			elif re.search(r"\((tt\d+)\)",line): #如果能從資料夾名稱找到IMDbID
				MainID = re.search(r"\((tt\d+)\)",line).group(1)
			else:
				print(line)
				continue
			reList = [MainID] + part1 + part2 + [part3]
			List += [reList]
	return List

def input(db_name,table_name,List,many=False,replace=False):
	num = len(List[0]) if many else len(List)
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()
	pattern = "IGNORE" if not replace else "REPLACE"
	execute = 'INSERT OR %s INTO %s VALUES (?%s)' % (pattern,table_name,",?"*(num-1))
	if many : #如果是批量資料(蜂巢迴圈)
		cursor.executemany(execute,List)
	else:
		cursor.execute(execute,List)
	conn.commit()
	cursor.close()
	conn.close()

def output(db_name,table_name,file_name):
	with open(file_name, "w", encoding = 'utf-8-sig') as write_file:
		conn = sqlite3.connect(db_name)
		cursor = conn.cursor()
		execute = "SELECT * FROM %s" % (table_name)
		for row in cursor.execute(execute):
			writeRow = "\t".join('%s' % r for r in row)+"\n"
			write_file.write(writeRow)
def query(db_name,table_name,sid):
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()
	execute = "SELECT * From %s WHERE SID = ?" % (table_name)
	result = cursor.execute(execute, [sid]).fetchone()
	cursor.close()
	conn.close()
	return result
def delete(db_name,table_name,sid):
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()
	execute = "DELETE From %s WHERE SID = ?" % (table_name)
	result = cursor.execute(execute, [sid])
	conn.commit()
	cursor.close()
	conn.close()




'''
db_name = "LCU.db"
table_name = "Data"
init(db_name, table_name)

#匯出用
#output(db_name,table_name,"Movie.tsv")

#匯入用
List = build_tsv("IN.tsv")
input(db_name,table_name,List,many=True,replace=True)'''
