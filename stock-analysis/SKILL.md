---
name: stock-analysis
description: 日経平均・クルーズ(2138)・ドル円・NYダウ・NASDAQの現在株価・前日比・変動要因を分析する。「株価」「stock」「日経」「マーケット」などのリクエストでこのスキルを使用すること。引数で銘柄を追加指定することも可能。
---

# 本日の株価変動要因分析

引数で追加銘柄が指定された場合はその銘柄も含めて分析すること。

## 1. 株価の取得（すべて並行実行）

以下の銘柄について **現在値・前日終値・前日比・前日比(%)・データ時点** を取得する。
**WebSearchは過去データを返すことがあるため使用禁止。すべてWebFetchで直接取得すること。**

### 日経平均株価
- Step1: `https://finance.yahoo.co.jp/quote/998407.O` をWebFetch
  - 「現在値」「前日比」「前日比(%)」「データ時刻」を抜き出す
- Step2（失敗時）: `https://kabutan.jp/stock/?code=998407` をWebFetch

### ドル円（USD/JPY）
- `https://kabutan.jp/stock/kabuka?code=0950` をWebFetch
  - 「現在値」「前日比」「前日比(%)」「データ時刻」を抜き出す

### NYダウ（Dow Jones Industrial Average）
- `https://us.kabutan.jp/indexes/%5EDJI` をWebFetch
  - 「現在値」「前日比」「前日比(%)」「データ時刻」を抜き出す

### NASDAQ総合指数
- `https://us.kabutan.jp/indexes/%5EIXIC` をWebFetch
  - 「現在値」「前日比」「前日比(%)」「データ時刻」を抜き出す

### 個別銘柄（クルーズ 2138、および引数で追加された銘柄）
- Step1: `https://kabutan.jp/stock/?code=XXXX` をWebFetch（XXXXは証券コード）
  - 「現在値」「前日比」「前日比(%)」「前日終値」「データ時刻」を抜き出す
- Step2（失敗時）: `https://finance.yahoo.co.jp/quote/XXXX.T` をWebFetch

⚠️ 取得できなかった場合は「取得不可」とせず、取得できた直近値と取得日時を明示して記載すること。

## 2. 分析テキストの作成

以下のフォーマットでテキストを組み立てる（Chatwork通知にも使用する）:

```
【本日の株価変動要因分析】YYYY/MM/DD HH:MM

■ 株価サマリー
日経平均:   XX,XXX円  前日比 +/-XXX (+/-X.XX%)  [HH:MM]
ドル円:     XXX.XX円  前日比 +/-X.XX (+/-X.XX%)  [HH:MM]
NYダウ:     XX,XXX    前日比 +/-XXX (+/-X.XX%)  [前日終値]
NASDAQ:     X,XXX     前日比 +/-XXX (+/-X.XX%)  [前日終値]
クルーズ(2138): XXX円  前日比 +/-X (+/-X.XX%)   [HH:MM]

■ 変動要因（日経平均）
・XXXXX
・XXXXX
・XXXXX

■ 変動要因（個別銘柄）
【クルーズ(2138)】
・XXXXX（または「個別材料なし・地合いに連動」）
```

## 3. 変動要因の分析

WebSearch で当日のマーケットニュースを検索し、各銘柄の変動要因を調査する。
- 日経平均: 米国市場動向、為替、経済指標、地政学リスクなど
- 個別銘柄: 決算、IR、セクター動向など。特段のニュースがなければ「個別材料なし・地合いに連動」

分析は銘柄ごとに箇条書き3-5項目で簡潔に。

