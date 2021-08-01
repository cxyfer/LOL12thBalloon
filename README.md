# LOL12thBalloon - LOL週年活動搶氣球程式

## balloon.exe
仰賴圖片辨識，會因使用者顯示設定而需個別設定

### 環境
- LOL大廳解析度：**1280*720**
- Windows顯示比例：**125%**
- 需以**管理員**身分執行

### 功能
- 爬取Garena新聞下方的最新評論，並輸入序號
- 搶完60顆氣球後自動兌換獎勵（需圖資支持）
- 完成後自動停止並播放通知，大約10分鐘可以搶完60顆氣球

### 個人化
- 若使用者無法和開發環境相同，可自行截圖並替換以下檔案
  - confirm.png
  - inBox1.png
  - inBox2.png
  - submit1.png
  - submit2.png

## balloonCMD.exe
使用token執行，需自行取得token

### 使用說明
1. 開啟LOL主程式並進入活動頁面
2. 開啟 `C:\Garena\Games\32775\Game\Logs\LeagueClient Logs` 資料夾（請自行依安裝路徑調整）
3. 使用記事本打開最新的_LeagueClient.log文件
![](https://i.imgur.com/B8p9Tp2.png)
4. 在其中搜尋 `https://bargain.lol.garena.tw/?token=`
![](https://i.imgur.com/09ndWug.png)
5. 複製網址貼上到程式中