# ptt_crawler
本爬蟲實現部分的功能（尚未完成存入資料庫部分）


執行
```
python server.py
python worker.py
```
- 本程式會建立一個存放task的queue,以及得到worker計算回復的queue。預設ip＝127.0.0.1，port=5000, password=abc，可在local端開啟一個 server.py 與多個terminal執行 worker.py
- sever檢查目錄中是否有所有看板的目錄，如果有目錄，則會將看板的首頁url放入queue中 (程式碼中，僅測試放入100個首頁)，等待worker接收
    - 如果沒有看板目錄則會經由url＝'https://www.ptt.cc/cls/1' 進入分類看板首頁依照每個節點爬出group中所包含的看板，並建立檔案，**以概括大部分的分類看板**

- 接著進入等待worker回報的模式，此階段每五秒監聽一次由worker回傳的訊息，並統整資訊
    - worker會將process id，以及正在處理的看板(目前用random模擬符合的文章數目)
    - server會把相同的pid資訊過濾，只留下一條最新的紀錄，並記錄所有正在工作的worker和有連線過的worker，因此這個功能可以用來監控是否有worker離線或終止工作

執行畫面
---
- 先執行server等待連線
![](https://i.imgur.com/mr5dqgU.png)
- 再開啟兩個worker，兩邊分別會處理各自的看板(print出來)
![](https://i.imgur.com/iiXxkix.png)
- server端會收到兩個worker的資訊 (process id作為識別用)
![](https://i.imgur.com/UTfFJVN.png)
- 如果關閉其中的worker則會出現missing worker提示，**此情況定義為一種異常通知**
- ![](https://i.imgur.com/lzTnAL8.png)

## crawler.py
執行
```
python3 crawler.py
```
- 用date = "2020-02-24 2020-02-25" 作為query的測試
- 用WomenTalk版測試
- 每進到一個頁面，先爬取所有文章的資訊，以及前一頁的連結
    - 對每篇文章用一個fuction去爬出所需內容，若文章被刪除則不處理
    - 依序檢查po文時間，向前一頁可得到更早的時間之文章，如果遇到比query還早的文章，表示不用再往前翻頁了

- 符合條件的文章會印出titie, 並且以title, authorId, publishedTime三項組成一個tuple計算**hash值作為key**, 確保資料庫的資料是唯一的
- 用過的query之時間用datetime格式存入檔案，以便後續檢查維護是否已經成功擷取

執行畫面
---

![](https://i.imgur.com/D9ocigs.png)
