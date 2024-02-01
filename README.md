# darts-pro-tour-schedule

ダーツプロツアーの大会日程を`iCalendar`([RFC 5545](https://datatracker.ietf.org/doc/html/rfc5545))形式で提供し定期的に更新する為のレポジトリ。
本レポジトリから提供しているスケジュールは非公式なものであり、ベストエフォートで提供されています。正式な大会日程や詳細などは、各プロ団体が公開している資料を参照してください。

## 対応状況

現在以下のプロ団体の大会日程に対応してる。

- [PERFECT](https://www.prodarts.jp/)
- [JAPAN](https://japanprodarts.jp/)

## 利用方法

`calendars/`にある`.ics`ファイルをカレンダーアプリに落とし込むか、ファイルURL (例: https://raw.githubusercontent.com/Hsn723/darts-pro-tour-schedule/master/calendars/perfect.ics )を用いてカレンダーアプリに追加する。ファイル読み込みの場合、読み込み以降に更新は反映されないのでご注意ください。
