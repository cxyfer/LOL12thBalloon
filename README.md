# LOL12thBalloon - LOL週年活動搶氣球程式

> 使用自動程式皆有風險，請自行評估是否使用

## balloon.exe
仰賴圖片辨識，會因使用者顯示設定而需個別設定

### 環境
- LOL大廳解析度：**1280*720**
- Windows顯示比例：**125%**
- 需以**管理員**身分執行

### 功能
- 爬取Garena新聞下方的最新評論，並輸入序號
- 搶完60顆氣球後自動兌換獎勵（**需**圖資支持）
- 完成後自動停止並播放通知，大約**10分鐘**可以搶完60顆氣球

### 個人化
- 若使用者無法和開發環境相同，可自行截圖並替換以下檔案
  - confirm.png
  - inBox1.png
  - inBox2.png
  - submit1.png
  - submit2.png

## balloonCMD.exe (恢復使用)
使用token在背景執行，需自行取得token

### 功能
- 爬取Garena新聞下方的最新評論，並輸入序號
- 搶完60顆氣球後自動兌換獎勵（背景執行，**不需**圖資支持）
- 完成後自動停止並播放通知，大約**3分鐘**可以搶完60顆氣球

### 使用說明
1. 開啟LOL主程式並**進入活動頁面**
2. 打開程式，若無法自動獲取token請輸入LOL安裝路徑下`LeagueClient Logs`資料夾之完整路徑，如 `C:\Garena\Games\32775\Game\Logs\LeagueClient Logs`（請自行依安裝路徑調整）

### ~~獲取token~~ (已改為自動獲取token)
1. 開啟LOL主程式並進入活動頁面
2. 開啟 `C:\Garena\Games\32775\Game\Logs\LeagueClient Logs` 資料夾（請自行依安裝路徑調整）
3. 使用記事本打開最新的 `_LeagueClientUx.log` 文件
![](https://i.imgur.com/NUZV33G.png)
4. 在其中搜尋 `https://bargain.lol.garena.tw/?token=`
![](https://i.imgur.com/ZQNwUbU.png)
5. 複製網址貼上到程式中