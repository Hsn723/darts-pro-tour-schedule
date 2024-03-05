# darts-pro-tour-schedule

ダーツプロツアーの大会日程を`iCalendar`([RFC 5545](https://datatracker.ietf.org/doc/html/rfc5545))形式で提供し定期的に更新する為のレポジトリ。
本レポジトリから提供しているスケジュールは非公式なものであり、ベストエフォートで提供されています。正式な大会日程や詳細などは、各プロ団体が公開している資料を参照してください。

## 対応状況

現在以下のプロ団体の大会日程に対応してる。

- [PERFECT](https://www.prodarts.jp/)
- [JAPAN](https://japanprodarts.jp/)
- [D-TOUR](https://www.da-topi.jp/)

## 利用方法

`calendars/`にある`.ics`ファイルをカレンダーアプリに落とし込むか、ファイルURL (例: https://raw.githubusercontent.com/Hsn723/darts-pro-tour-schedule/master/calendars/perfect.ics )を用いてカレンダーアプリに追加する。ファイル読み込みの場合、読み込み以降に更新は反映されないのでご注意ください。

### 事前準備

`calendars/`にある`.ics`ファイルのテキスト表示(Raw)URLを取得する:

- PERFECTの場合: `https://raw.githubusercontent.com/Hsn723/darts-pro-tour-schedule/master/calendars/perfect.ics`
- JAPANの場合: `https://raw.githubusercontent.com/Hsn723/darts-pro-tour-schedule/master/calendars/japan.ics`
- D-TOURの場合: `https://raw.githubusercontent.com/Hsn723/darts-pro-tour-schedule/master/calendars/d-tour.ics`

そのURLを控えてお使いになる暦アプリに適宜追加することで自動更新されます(以下参考例)。

### Outlookの場合

#### カレンダー画面で「予定表を追加」をクリックする

![outlook-01](https://github.com/Hsn723/darts-pro-tour-schedule/assets/1885220/6fd1590e-4e93-4c6e-8bd2-66cedb7a1a49)

#### 「Webから定期受診」をクリックし、事前準備で控えたカレンダーURLを入力する

![outlook-02](https://github.com/Hsn723/darts-pro-tour-schedule/assets/1885220/108ac87d-018a-4861-9d05-39274aa730b5)

#### 追加したカレンダーに名前や色、アイコン等を設定しインポートボタンを押す

![outlook-03](https://github.com/Hsn723/darts-pro-tour-schedule/assets/1885220/e1895a33-1416-4d9d-82ce-b62f06566c9b)

### Apple Mailの場合

#### カレンダーアプリを開いて下部の「カレンダー」ボタンをクリックする

![20240209_022348000_iOS](https://github.com/Hsn723/darts-pro-tour-schedule/assets/1885220/7d1bac25-f717-4ed7-b76f-4e04e05cd0b8)

#### 「カレンダー追加」をクリックする

![20240209_022354000_iOS](https://github.com/Hsn723/darts-pro-tour-schedule/assets/1885220/05dadc36-4487-44e9-9983-c3f18c89a664)

#### 「照会カレンダーを追加」をクリックする

![20240209_022359000_iOS](https://github.com/Hsn723/darts-pro-tour-schedule/assets/1885220/6de1935c-7b0f-4ec3-b15e-b17e10ba6456)

#### 事前準備で控えたカレンダーURLを入力し追加する

![20240209_022403000_iOS](https://github.com/Hsn723/darts-pro-tour-schedule/assets/1885220/72e9cc6c-b769-40c6-83ea-3c7c11744759)
