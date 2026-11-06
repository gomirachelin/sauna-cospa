# GOMIRACHELIN（コスパで選ぶ、全国サウナ正直ガイド）

## ⚠️ 重要：現在の公開先と CNAME に関する注意（2026-10-08〜11-02更新）

- **Do NOT add a CNAME to kenji0618y.github.io or gomirachelin/sauna-cospa. The public site is hosted at https://gomirachelin.github.io/sauna-cospa/ (repo: gomirachelin/sauna-cospa).**
- 2026-10-06 に `kenji0618y.github.io` へ `CNAME`（sauna-cospa.com）を足したところ、GitHubの仕様で同じアカウントのプロジェクトサイト（kekkon-roadmap・henshu-lock）まで `sauna-cospa.com/〜` へ転送され、結婚ロードマップの端末データとLINE通知が見えなくなった（公式：https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages ）。
- 2026-10-08 にサウナのサイト（GOMIRACHELIN）を別リポジトリへ分離し、2026-10-22 に月額・年額費用ゼロで運用するため独自ドメイン `sauna-cospa.com` を外して GitHub Pages の無料アドレスへ切り替えた（ConoHa WING 自動更新OFF済み）。
- 2026-11-02 に公開リポジトリを個人 `kenji0618y` から組織 `gomirachelin`（**https://github.com/gomirachelin/sauna-cospa**）へ移設した。現在の正式な公開URLは **https://gomirachelin.github.io/sauna-cospa/**（サイト内の内部パスは `/sauna-cospa/〜`）。
- 旧URLからの転送は専用リポジトリで維持している（`kenji0618y/sauna-cospa`・`kenji0618y/sauna-cospa-com-redirect`・`kenji0618y/kenji0618y.github.io`）。

## 概要

- **公開URL**: [https://gomirachelin.github.io/sauna-cospa/](https://gomirachelin.github.io/sauna-cospa/)
- **正本リポジトリ**: [https://github.com/gomirachelin/sauna-cospa](https://github.com/gomirachelin/sauna-cospa)
- **公開のしくみ**: このリポジトリの `main` ブランチへ反映（push）すると、GitHub Pages でそのまま本番公開されます（ConoHa サーバーへのアップロードは不要です）。
- **AIで作業するとき**: `AGENTS.md` と `docs/STATE.md` を最初に読み、作業のたびに記録を更新してください。

## 主なファイルとフォルダ

| パス | 内容 |
|------|------|
| `index.html` | トップページ |
| `{スラッグ}/index.html` | 各サウナ施設のレビュー・固定ページ |
| `ランキング/index.html` | 全国コスパランキング（`scripts/build_rankings.py` で生成） |
| `10項目別ランキング/index.html` | 10項目別の順位一覧（`scripts/build_rankings.py` で生成） |
| `reviews/index.html` | レビュー一覧（`scripts/gen_reviews.py` で生成） |
| `map/index.html` | ログイン不要の全国サウナ地図（`scripts/build_map_data.py` で生成） |
| `sauna-daigaku.html` / `sauna-university/` | サウナ大学（カリキュラム・学習コンテンツ） |
| `css/site.css` | 黒×金の共通ヘッダー / ナビ / フッター |
| `data/rankings.json` | ランキング・10項目スコアの正本データ |
| `data/map-facilities.json` | サウナ地図の施設・座標の正本データ |
| `data/urls.json` / `data/url-history.json` | 現在公開中のページURL一覧と旧URL履歴 |
| `sitemap.xml` / `robots.txt` | 検索エンジン向けのサイトマップと設定 |
| `docs/` | サイトの現状（`STATE.md`）、ロードマップ（`GitHub移行ロードマップ.md` / `roadmap.html`）、各種手順書 |

ナビメニュー: トップ / WHY / ランキング / サウナ大学 / サウナ地図 / お問い合わせ（トップページの「レビュー一覧を見る」から `/sauna-cospa/reviews/` へ移動できます）。
