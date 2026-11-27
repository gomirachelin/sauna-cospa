# -*- coding: utf-8 -*-
"""各ページへ共有用の情報（OGP・Twitter・構造化データ）を入れる。

使い方（サイトのフォルダで）:
    python3 scripts/seo_meta.py

レビュー一覧を作り直す scripts/gen_reviews.py からも apply_document を呼ぶ。
本文・見た目の見出し（h1）は変えない。変えるのは title と説明文、共有用タグ。
"""
import html
import json
import os
import re
import subprocess
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = "https://gomirachelin.github.io"
PREFIX = "/sauna-cospa"
SITE = ORIGIN + PREFIX + "/"
OG_IMAGE = SITE + "assets/images/og-default.png"
OG_ALT = "GOMIRACHELIN — コスパで選ぶ、全国サウナ正直ガイド"
ORG_NAME = "GOMIRACHELIN"
TODAY = "2026-11-25"

# 検索結果用のタイトル。画面上の h1 はそのまま。
TITLES = {
    "index.html": "GOMIRACHELIN｜コスパで選ぶ全国サウナ正直ガイド",
    "why/index.html": "なぜこのサイトを作ったか（WHY）｜GOMIRACHELIN",
    "how/index.html": "採点の仕方（HOW）｜10項目とコスパの測り方 — GOMIRACHELIN",
    "ランキング/index.html": "全国サウナコスパランキング｜GOMIRACHELIN",
    "10項目別ランキング/index.html": "10項目別ランキング｜サウナ・水風呂・休憩の順位 — GOMIRACHELIN",
    "reviews/index.html": "サウナ正直レビュー一覧｜GOMIRACHELIN",
    "map/index.html": "エリアから探す｜都道府県・宿泊・ふるさと納税 — GOMIRACHELIN",
    "world/index.html": "海外サウナガイド（WORLD）｜GOMIRACHELIN",
    "sauna-university/index.html": "サウナ大学｜入り方からととのうの科学まで — GOMIRACHELIN",
    "sauna-daigaku.html": "サウナ大学｜4段階で学ぶ無料のサウナ教科書 — GOMIRACHELIN",
    "サウナハット-サウナマット/index.html": "サウナハット・サウナマットおすすめ比較｜GOMIRACHELIN",
    "お問い合わせ/index.html": "お問い合わせ｜GOMIRACHELIN",
    "運営者情報/index.html": "運営者情報｜GOMIRACHELIN",
    "プライバシーポリシー/index.html": "プライバシーポリシー｜GOMIRACHELIN",
    "免責事項/index.html": "免責事項｜GOMIRACHELIN",
    "404.html": "ページが見つかりません｜GOMIRACHELIN",
    "category/review/index.html": "レビュー一覧へ移動しました｜GOMIRACHELIN",
}

DESCRIPTIONS = {
    "index.html": "施設の肩書きではなく、払ったお金と過ごした時間でサウナを選ぶための正直ガイド。全国ランキング、エリア検索、レビュー、サウナ大学へ進めます。",
    "why/index.html": "殿堂入りの名店で打ちのめされた体験から、GOMIRACHELINを始めた理由。忖度せず、貶めず、あなたの一日を守るために書いています。",
    "how/index.html": "GOMIRACHELINの採点方法。コスパの考え方と、サウナ室・水風呂・休憩・動線・ロウリュ・施設・清潔さ・独自性・ホスピタリティの10項目を説明します。",
    "ランキング/index.html": "実際に訪問して10項目で採点した全国サウナのコスパランキング。総合・コスパ・タイパで並び替え、都道府県や宿泊・ふるさと納税でも絞り込めます。",
    "10項目別ランキング/index.html": "サウナ室、水風呂、休憩、動線、ロウリュなど10の評価項目ごとに、全国サウナの順位を見られます。",
    "reviews/index.html": "GOMIRACHELINが実際に訪問して10項目で採点したサウナ正直レビューの一覧。新着順に、総合・コスパ・タイパのスコアを掲載しています。",
    "map/index.html": "掲載サウナを、地方・都道府県・海外、宿泊できる宿（楽天トラベル）、ふるさと納税から探せます。",
    "world/index.html": "GOMIRACHELINが現地で10項目採点した海外サウナ・スパのガイド。国ごとに正直な点数と特徴を掲載しています。",
    "sauna-university/index.html": "サウナの入り方、マナー、ととのう仕組み、水風呂、ロウリュ、歴史と文化、熱の物理学までを無料で学べるサウナ大学です。",
    "sauna-daigaku.html": "下段（初級）から中段・上段・ストーブ前（マスター）まで4段階。資格、熱の物理学、水風呂、ととのうの科学、世界のサウナ文化、サ飯、聖地巡礼、経営まで学べる無料教材です。",
    "サウナハット-サウナマット/index.html": "サウナハットとサウナマットを、自分で比べてそのまま買える比較ページです。個別の愛用品は準備中でも、Amazonと楽天の検索から今すぐ選べます。",
    "お問い合わせ/index.html": "ご意見・ご感想、記事への指摘、掲載のご相談、取材のご依頼は、GOMIRACHELINのお問い合わせフォームから送れます。",
    "プライバシーポリシー/index.html": "個人情報の利用目的、広告、アクセス解析（Googleアナリティクス）の取り扱いを定めたGOMIRACHELINのプライバシーポリシーです。",
    "免責事項/index.html": "料金・営業時間・設備などの掲載情報は訪問または執筆時点のものです。最新情報は各施設にご確認ください。",
    "運営者情報/index.html": "GOMIRACHELIN（ゴミラシュラン）は、全国のサウナをコスパで正直にレビューするサイトです。施設と利害関係のない一般人が運営しています。",
    "サウナのふるさと納税｜実質2000円でととのう、コ/index.html": "サウナ好きのためのふるさと納税ガイド。実質2,000円でととのえる返礼品の考え方と、掲載施設の宿泊・返礼の入り口をまとめています。",
    "404.html": "お探しのページは見つかりませんでした。アドレスが変わった場合は、トップまたはレビュー一覧から目的のページを開けます。",
    "kekkon-check/index.html": "この端末に残っているかを、この画面の中だけで確認するページです。",
    "category/review/index.html": "レビューの古いアドレスです。サウナ正直レビューの一覧へ移動します。",
}

COLUMN_REL = "サウナのふるさと納税｜実質2000円でととのう、コ/index.html"
SITEMAP_SKIP = {
    "404.html",
    "kekkon-check/index.html",
    "オアシスサウナ-アスティル-2/index.html",
    "上野ステーションホステル-オリエンタル2-2/index.html",
    "category/review/index.html",
}
# 解析タグを足さないページ（転送・確認用・元から解析なし）
GA_SKIP = SITEMAP_SKIP

# サウナ大学の章データ。main() が埋める。gen_reviews から呼ぶときは空のままでよい。
COURSE_PARTS = None


def load_urls():
    path = os.path.join(ROOT, "data", "urls.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def quote_path(path):
    """/sauna-cospa/日本語/ をサイトマップ用のエンコードにする。"""
    parts = path.split("/")
    return "/".join(quote(p, safe="").lower() if p else "" for p in parts)


def canonical_from_rel(rel):
    rel = rel.replace("\\", "/")
    if rel == "index.html":
        return SITE
    if rel == "sauna-daigaku.html":
        return SITE + "sauna-daigaku.html"
    if rel == "404.html":
        return SITE + "404.html"
    if rel.endswith("/index.html"):
        slug = rel[: -len("index.html")]
        return SITE + quote_path(slug).lstrip("/")
    return SITE + quote_path(rel).lstrip("/")


def existing_canonical(text):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', text)
    return m.group(1) if m else None


def existing_title(text):
    m = re.search(r"<title>(.*?)</title>", text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def existing_description(text):
    m = re.search(r'<meta name="description" content="(.*?)"', text, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def existing_h1(text):
    # script の中のテンプレートも拾うので、最初の実タグに限る
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()


def is_noindex(text):
    m = re.search(r'<meta name="robots" content="([^"]+)"', text, re.I)
    return bool(m and "noindex" in m.group(1).lower())


def review_description(name, desc):
    d = re.sub(r"\s+", " ", desc or "").strip()
    total = None
    m = re.search(r"総合\s*([0-9]+(?:\.[0-9]+)?)", d)
    if m:
        total = m.group(1)
    else:
        m = re.search(r"PERFORMANCE:\s*([0-9]+)", d)
        if m:
            total = m.group(1)
    cospa = None
    m = re.search(r"コスパ\s*([0-9]+(?:\.[0-9]+)?)", d)
    if not m:
        m = re.search(r"COSPA:\s*([0-9]+(?:\.[0-9]+)?)", d)
    if m:
        cospa = m.group(1)
    price = None
    m = re.search(r"平日¥\s*([0-9,]+)", d)
    if m:
        price = m.group(1)
    place = None
    m = re.match(r"([^／]{1,16})／", d)
    if m and "PERFORMANCE" not in d[:24]:
        place = m.group(1).strip()
    elif "名古屋" in d:
        place = "名古屋"
    grade = None
    for g in ("神コスパ", "高コスパ", "普通", "コスパ低"):
        if g in d:
            grade = g
            break
    if not total and not price:
        return d
    head = f"{name}を実際に訪れて採点した正直レビューです。"
    if place:
        head = f"{place}の{name}を実際に訪れて採点した正直レビューです。"
    extra = []
    if price:
        extra.append(f"平日{price}円")
    if total:
        extra.append(f"総合{total}点")
    if cospa:
        extra.append(f"コスパ{cospa}")
    if grade:
        extra.append(grade)
    if extra:
        head += "、".join(extra) + "。"
    return head


def page_kind(rel, text):
    if rel in ("index.html",):
        return "home"
    if rel == "sauna-daigaku.html":
        return "course"
    if rel == COLUMN_REL:
        return "article"
    if rel in (
        "why/index.html",
        "how/index.html",
        "サウナハット-サウナマット/index.html",
        "ランキング/index.html",
        "10項目別ランキング/index.html",
        "reviews/index.html",
        "map/index.html",
        "world/index.html",
        "sauna-university/index.html",
        "お問い合わせ/index.html",
        "運営者情報/index.html",
        "プライバシーポリシー/index.html",
        "免責事項/index.html",
        "404.html",
        "kekkon-check/index.html",
        "category/review/index.html",
    ):
        return "webpage"
    if is_noindex(text) or "http-equiv=\"refresh\"" in text or 'http-equiv="refresh"' in text:
        return "redirect"
    if rel.endswith("/index.html"):
        return "review"
    return "webpage"


def org_node():
    return {
        "@type": "Organization",
        "@id": SITE + "#organization",
        "name": ORG_NAME,
        "url": SITE,
        "logo": {"@type": "ImageObject", "url": OG_IMAGE},
        "description": "コスパで選ぶ、全国サウナの正直レビューメディア",
    }


def website_node():
    return {
        "@type": "WebSite",
        "@id": SITE + "#website",
        "name": ORG_NAME,
        "url": SITE,
        "inLanguage": "ja",
        "description": DESCRIPTIONS["index.html"],
        "publisher": {"@id": SITE + "#organization"},
    }


def score_from(desc):
    d = desc or ""
    m = re.search(r"総合\s*([0-9]+(?:\.[0-9]+)?)", d)
    if m:
        return m.group(1)
    m = re.search(r"PERFORMANCE:\s*([0-9]+)", d)
    if m:
        return m.group(1)
    return None


def jsonld_for(rel, kind, title, desc, canonical, h1, dates):
    graph = []
    if kind == "home":
        graph = [org_node(), website_node()]
    elif kind == "course":
        course = {
            "@type": "Course",
            "name": "サウナ大学",
            "description": desc,
            "url": canonical,
            "inLanguage": "ja",
            "isAccessibleForFree": True,
            "provider": {"@id": SITE + "#organization"},
        }
        if COURSE_PARTS:
            course["hasPart"] = COURSE_PARTS
        graph = [org_node(), course]
    elif kind == "article":
        graph = [
            org_node(),
            {
                "@type": "Article",
                "headline": h1 or title,
                "description": desc,
                "inLanguage": "ja",
                "mainEntityOfPage": canonical,
                "url": canonical,
                "image": OG_IMAGE,
                "author": {"@id": SITE + "#organization"},
                "publisher": {"@id": SITE + "#organization"},
                "datePublished": dates.get(rel),
            },
        ]
    elif kind == "review":
        rating = score_from(desc)
        review = {
            "@type": "Review",
            "name": title,
            "url": canonical,
            "inLanguage": "ja",
            "description": desc,
            "author": {"@id": SITE + "#organization"},
            "publisher": {"@id": SITE + "#organization"},
            "itemReviewed": {
                "@type": "HealthAndBeautyBusiness",
                "name": h1 or title,
            },
        }
        if dates.get(rel):
            review["datePublished"] = dates[rel]
        if rating:
            review["reviewRating"] = {
                "@type": "Rating",
                "ratingValue": rating,
                "bestRating": "100",
                "worstRating": "0",
            }
        crumb = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": "レビュー", "item": SITE + "reviews/"},
                {"@type": "ListItem", "position": 3, "name": h1 or title, "item": canonical},
            ],
        }
        graph = [org_node(), review, crumb]
    else:
        graph = [
            org_node(),
            {
                "@type": "WebPage",
                "name": title,
                "description": desc,
                "url": canonical,
                "inLanguage": "ja",
                "isPartOf": {"@id": SITE + "#website"},
                "publisher": {"@id": SITE + "#organization"},
            },
        ]
    # datePublished が無い記事はキーを落とす
    for node in graph:
        if node.get("datePublished") in (None, ""):
            node.pop("datePublished", None)
    data = {"@context": "https://schema.org", "@graph": graph}
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    return raw.replace("<", "\\u003c")


def seo_block(title, desc, canonical, kind):
    og_type = "article" if kind in ("review", "article", "course") else "website"
    esc = lambda s: html.escape(s, quote=True)
    lines = [
        "<!-- seo:start -->",
        '<meta property="og:locale" content="ja_JP">',
        f'<meta property="og:site_name" content="{ORG_NAME}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{esc(canonical)}">',
        f'<meta property="og:image" content="{OG_IMAGE}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(OG_ALT)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        f'<meta name="twitter:image" content="{OG_IMAGE}">',
        '<link rel="icon" href="/sauna-cospa/sauna-icon-180.png">',
        "<!-- seo:end -->",
    ]
    return "\n".join(lines)


def set_title(text, title):
    esc = html.escape(title)
    if re.search(r"<title>.*?</title>", text, re.S):
        return re.sub(r"<title>.*?</title>", f"<title>{esc}</title>", text, count=1, flags=re.S)
    return text.replace("</head>", f"<title>{esc}</title>\n</head>", 1)


def set_description(text, desc):
    esc = html.escape(desc, quote=True)
    tag = f'<meta name="description" content="{esc}">'
    if re.search(r'<meta name="description" content=".*?"\s*/?>', text, re.S):
        return re.sub(
            r'<meta name="description" content=".*?"\s*/?>',
            tag,
            text,
            count=1,
            flags=re.S,
        )
    return re.sub(r"</title>", "</title>\n  " + tag, text, count=1)


def set_canonical(text, url):
    tag = f'<link rel="canonical" href="{html.escape(url, quote=True)}">'
    if re.search(r'<link rel="canonical" href="[^"]*">', text):
        return re.sub(r'<link rel="canonical" href="[^"]*">', tag, text, count=1)
    if re.search(r'<meta name="description" content=".*?"\s*/?>', text, re.S):
        return re.sub(
            r'(<meta name="description" content=".*?"\s*/?>)',
            r"\1\n  " + tag,
            text,
            count=1,
            flags=re.S,
        )
    return re.sub(r"</title>", "</title>\n  " + tag, text, count=1)


def choose_title(rel, text, kind):
    if rel in TITLES:
        return TITLES[rel]
    h1 = existing_h1(text)
    if kind == "redirect" and h1:
        return f"{h1}のページを移動しました｜GOMIRACHELIN"
    if kind == "review" and h1:
        return f"{h1}の正直レビュー｜GOMIRACHELIN"
    return existing_title(text)


def choose_description(rel, text, kind, title):
    if rel in DESCRIPTIONS:
        return DESCRIPTIONS[rel]
    current = existing_description(text)
    h1 = existing_h1(text)
    if kind == "redirect" and h1:
        if current.startswith("このアドレスは移動しました"):
            return current
        return f"このアドレスは移動しました。{h1}の正直レビューは新しいURLで読めます。"
    if kind == "review":
        # すでに文章化済みなら、もう一度採点メモとして読み直さない（料金表記が落ちる）
        if "正直レビューです" in current:
            return current
        return review_description(h1 or title, current)
    if current and "…" not in current and "[…]" not in current:
        return current
    return current or title


def apply_document(text, rel, dates=None):
    """1ページ分の HTML 文字列に、共有用タグと検索用の title・説明を入れる。"""
    dates = dates if dates is not None else {}
    kind = page_kind(rel, text)
    # 転送ページの canonical は移動先のまま維持する（urls と揃っている）
    canonical = existing_canonical(text) or canonical_from_rel(rel)
    title = choose_title(rel, text, kind)
    # 説明文は、タイトル反映前の本文情報を使う
    desc = choose_description(rel, text, kind, title)
    h1 = existing_h1(text)
    text = set_title(text, title)
    text = set_description(text, desc)
    text = set_canonical(text, canonical)
    block = seo_block(title, desc, canonical, kind)
    ld = jsonld_for(rel, kind, title, desc, canonical, h1, dates)
    ld_tag = '<script type="application/ld+json">\n' + ld + "\n</script>"
    text = re.sub(r"\s*<!-- seo:start -->.*?<!-- seo:end -->\s*", "\n", text, flags=re.S)
    text = re.sub(
        r'\s*<script type="application/ld\+json">.*?</script>\s*',
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    replaced, n = re.subn(
        r'(<link rel="canonical" href="[^"]*">)\s*',
        lambda m: m.group(1) + "\n" + block + "\n" + ld_tag + "\n",
        text,
        count=1,
    )
    if n != 1:
        raise RuntimeError("canonical を入れられませんでした: " + rel)
    return replaced


def iter_html():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "docs", "scripts", "node_modules")]
        for name in filenames:
            if name.endswith(".html"):
                yield os.path.join(dirpath, name)


def rel_of(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def fix_world_links(text):
    text = text.replace('href=\\"/sauna-cospa/world/\\"', 'href="/sauna-cospa/world/"')
    text = re.sub(
        r'<li><a href="(?P<area>/sauna-cospa/map/)">AREA</a>\s*'
        r'<a href="(?P<world>/sauna-cospa/world/)">WORLD</a></li>',
        '<li><a href="\\g<area>">AREA</a></li>\n          <li><a href="\\g<world>">WORLD</a></li>',
        text,
    )
    return text


def fix_refresh(text):
    text = text.replace(
        'content="0; url=/オアシスサウナ-アスティル/"',
        'content="0; url=/sauna-cospa/オアシスサウナ-アスティル/"',
    )
    text = text.replace(
        'content="0; url=/上野ステーションホステル-オリエンタル2/"',
        'content="0; url=/sauna-cospa/上野ステーションホステル-オリエンタル2/"',
    )
    return text


def extract_course():
    """サウナ大学の章・用語を Node で取り出す。失敗したら None。"""
    script = """
const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync(process.argv[1], "utf8");
function grab(startMarker, endMarker) {
  const s = html.indexOf(startMarker);
  if (s < 0) throw new Error("missing " + startMarker);
  const e = html.indexOf(endMarker, s);
  if (e < 0) throw new Error("missing end " + startMarker);
  return html.slice(s, e);
}
const pieces = [
  grab("const CONTENT = ", "}; // === end CONTENT ===") + "}",
  grab("const GLOSSARY = ", "const SENSEI_KB"),
  grab("const ZEMI_LECTURES=", ";\\nfunction zemiLectureHTML"),
].join("\\n");
const tail = `
const chapters = CONTENT.chapters.map(ch => ({
  id: ch.id, tier: ch.tier, title: ch.title, subtitle: ch.subtitle || "", desc: ch.desc || "",
  lessons: (ch.lessons || []).map(ls => ({
    title: ls.title,
    headings: (ls.blocks || []).filter(b => b.type === "h").map(b => b.text)
  }))
}));
let quiz = 0;
CONTENT.chapters.forEach(ch => (ch.lessons || []).forEach(ls => { quiz += (ls.quiz || []).length; }));
const glossary = GLOSSARY.map(g => ({ t: g.t, r: g.r, d: g.d }));
const zemi = ZEMI_LECTURES.map(m => ({
  title: m.title, subtitle: m.subtitle || "", intro: m.intro || "",
  lessons: (m.lessons || []).map(l => l.title)
}));
process.stdout.write(JSON.stringify({ chapters, glossary, zemi, quiz }));
`;
vm.runInThisContext(pieces + "\\n" + tail);
"""
    path = os.path.join(ROOT, "sauna-daigaku.html")
    try:
        out = subprocess.check_output(["node", "-e", script, path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("サウナ大学の抽出に失敗しました")
        print(e.output.decode("utf-8", "replace")[:2000])
        return None
    return json.loads(out.decode("utf-8"))


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def esc(s):
    return html.escape(strip_tags(s), quote=True)


TIERS = [
    ("t1", "下段（初級）", "サウナデビューの基本、サ飯、聖地めぐり。"),
    ("t2", "中段（中級）", "ととのう科学、水風呂、ストーブ、設計、資格。"),
    ("t3", "上段（上級）", "世界の入浴文化、神話と禊、瞑想、テント・バレル。"),
    ("t4", "ストーブ前（マスター）", "熱の物理学、論文講読、経営学、小屋建築。"),
]


def curriculum_html(data):
    parts = []
    parts.append(
        '<section class="static-curriculum" id="curriculum-text" aria-label="カリキュラムと用語のテキスト版">'
        '<div class="wrap">'
        '<div class="eyebrow">TEXT INDEX</div>'
        '<h2 class="sec-title">カリキュラムと用語</h2>'
        '<p class="lead">章の名前、レッスンの見出し、用語を文章でも置いています。'
        'クイズ、修了証、質問は上のボタンからそのまま使えます。</p>'
    )
    by_tier = {}
    for ch in data["chapters"]:
        by_tier.setdefault(ch["tier"], []).append(ch)
    for tid, label, blurb in TIERS:
        chs = by_tier.get(tid) or []
        if not chs:
            continue
        parts.append(f"<h2>{esc(label)}</h2><p>{esc(blurb)}</p>")
        for ch in chs:
            parts.append(f'<article id="text-{esc(ch["id"])}">')
            parts.append(f"<h3>{esc(ch['title'])}</h3>")
            sub = " ".join(x for x in (ch.get("subtitle"), ch.get("desc")) if x)
            if sub:
                parts.append(f"<p>{esc(sub)}</p>")
            for ls in ch["lessons"]:
                parts.append(f"<h4>{esc(ls['title'])}</h4>")
                heads = [h for h in ls.get("headings") or [] if strip_tags(h)]
                if heads:
                    parts.append("<ul>")
                    for h in heads:
                        parts.append(f"<li>{esc(h)}</li>")
                    parts.append("</ul>")
            parts.append("</article>")
    if data.get("zemi"):
        parts.append("<h2>経営講座（ゼミ）</h2>")
        parts.append("<p>概要と40講のタイトルはどなたでも読めます。講義の本文は、経営ゼミ全体パック（税込3,000円）で読めます。</p>")
        parts.append('<p><a href="#zemi" onclick="go(\'zemi\');return false;">経営ゼミの概要と購入へ</a></p>')
        for mod in data["zemi"]:
            parts.append(f"<h3>{esc(mod['title'])}</h3>")
            if mod.get("subtitle"):
                parts.append(f"<p>{esc(mod['subtitle'])}</p>")
            if mod.get("intro"):
                parts.append(f"<p>{esc(mod['intro'])}</p>")
            if mod.get("lessons"):
                parts.append("<ul>")
                for title in mod["lessons"]:
                    parts.append(f"<li>{esc(title)}</li>")
                parts.append("</ul>")
    parts.append("<h2>サウナ用語辞典</h2>")
    parts.append("<dl>")
    for g in data["glossary"]:
        parts.append(f"<dt>{esc(g['t'])}<span>{esc(g['r'])}</span></dt><dd>{esc(g['d'])}</dd>")
    parts.append("</dl></div></section>")
    return "".join(parts)


def hero_html(data):
    lessons = sum(len(ch["lessons"]) for ch in data["chapters"])
    quiz = data.get("quiz") or 0
    gloss = len(data["glossary"])
    return f'''<section class="hero"><div class="wrap hero-inner">
    <div class="eyebrow">忖度なし・コスパで斬る GOMIRACHELIN 監修</div>
    <h1>サウナのすべてが、<br><span class="hl">ここで深く</span>学べる。</h1>
    <p class="sub">下段（初級）から、中段、上段、そしてストーブ前（マスター）へ。座席が上がるほど熱くなるように、学びも深くなる4段階カリキュラム。歴史・科学・資格・文化・熱の物理学まで、サウナの"すべて"が一つに。</p>
    <p class="by">権威や定説ではなく、自分の基準でサウナを選べる人を増やすために。すべての知識に出典付き。完全無料の学習教材。</p>
    <div class="cta-row">
      <button class="btn gold" onclick="go('learn')">学びを始める <span class="ar">→</span></button>
      <button class="btn ghost" onclick="go('quiz')">腕試しに挑戦</button>
      <a class="btn ghost" href="https://docs.google.com/forms/d/e/1FAIpQLSecstBtc6D7TJbwVgMfckm-nqPG86oogW3xNu6T56cMK5IqOw/viewform" target="_blank" rel="noopener">🎓 入学登録（無料）</a>
    </div>
    <div class="journey">
      <div class="jtitle">◆ ととのいの温度ジャーニー</div>
      <div class="jbar"></div>
      <div class="jsteps">
        <div class="jstep s1"><div class="n">STEP 01</div><div class="t">サウナ</div><small>体を温める</small></div>
        <div class="jstep s2"><div class="n">STEP 02</div><div class="t">水風呂</div><small>一気に冷やす</small></div>
        <div class="jstep s3"><div class="n">STEP 03</div><div class="t">外気浴</div><small>そして、ととのう</small></div>
      </div>
    </div>
    <div class="stats">
      <div class="stat"><b>4</b><span>段階</span></div>
      <div class="stat"><b id="statLessons">{lessons}</b><span>レッスン</span></div>
      <div class="stat"><b id="statQuiz">{quiz}</b><span>クイズ</span></div>
      <div class="stat"><b id="statGlossary">{gloss}</b><span>用語辞典</span></div>
    </div>
  </div></section>'''


CURRICULUM_CSS = """
.static-curriculum{padding:8px 0 64px}
.static-curriculum h2{font-family:var(--serif);font-weight:800;font-size:clamp(22px,3vw,32px);margin:28px 0 8px}
.static-curriculum h3{font-family:var(--serif);font-weight:800;font-size:22px;margin:22px 0 6px}
.static-curriculum h4{font-size:16px;margin:12px 0 4px;color:var(--gold-bright)}
.static-curriculum ul{margin:0 0 8px 1.2em;color:var(--cream-dim)}
.static-curriculum dt{font-weight:700;margin-top:14px}
.static-curriculum dt span{color:var(--muted);font-weight:500;margin-left:8px;font-size:13px}
.static-curriculum dd{color:var(--cream-dim);margin:2px 0 0}
"""


def patch_daigaku(text, data):
    text = re.sub(r'(?<!/sauna-cospa)/assets/images/', '/sauna-cospa/assets/images/', text)
    text = re.sub(
        r'if\("serviceWorker" in navigator && location\.protocol === "https:"\)\{\n'
        r'  navigator\.serviceWorker\.register\("/sauna-sw\.js", \{scope: "/sauna-daigaku\.html"\}\)\.catch\(\(\)=>\{\}\);\n'
        r'\}\n',
        "",
        text,
        count=1,
    )
    # 画面を描き直す処理が、最初から書いてある見出しまで消さないようにする
    text = text.replace(
        'document.getElementById("view-home").innerHTML=`',
        'document.getElementById("home-dynamic").innerHTML=`',
    )
    marker = 'document.getElementById("home-dynamic").innerHTML=`'
    idx = text.find(marker)
    if idx < 0:
        raise RuntimeError("サウナ大学のホーム描画が見つかりません")
    hero_at = text.find('<section class="hero">', idx)
    dash_at = text.find('<section class="section tight"><div class="wrap">\n    <div class="dash">', hero_at)
    if hero_at > 0 and dash_at > hero_at:
        text = text[:hero_at] + text[dash_at:]
    stat_snippet = (
        '  const doneTotal=S.done.length,allL=totalLessons();\n'
        '  const sl=document.getElementById("statLessons"); if(sl) sl.textContent=allL;\n'
        '  const sq=document.getElementById("statQuiz"); if(sq) sq.textContent=totalQuestions();\n'
        '  const sg=document.getElementById("statGlossary"); if(sg) sg.textContent=GLOSSARY.length;\n'
    )
    if 'getElementById("statLessons")' not in text:
        text = text.replace(
            '  const doneTotal=S.done.length,allL=totalLessons();\n',
            stat_snippet,
        )
    if ".static-curriculum{" not in text:
        text = text.replace("</style>", CURRICULUM_CSS + "</style>", 1)
    block = "<!-- crawl-curriculum:start -->" + curriculum_html(data) + "<!-- crawl-curriculum:end -->"
    if "<!-- crawl-curriculum:start -->" in text:
        text = re.sub(
            r"<!-- crawl-curriculum:start -->.*?<!-- crawl-curriculum:end -->",
            block,
            text,
            count=1,
            flags=re.S,
        )
    else:
        hero = hero_html(data)
        empty = '<section class="view" id="view-home"></section>'
        filled = (
            '<section class="view on" id="view-home">\n'
            + hero
            + '\n<div id="home-dynamic"></div>\n'
            + block
            + "\n</section>"
        )
        if empty not in text:
            raise RuntimeError("view-home の初期HTMLが見つかりません")
        text = text.replace(empty, filled, 1)
    return text


def course_parts_from(data):
    parts = []
    for ch in data["chapters"]:
        parts.append(
            {
                "@type": "LearningResource",
                "name": ch["title"],
                "description": ch.get("desc") or ch.get("subtitle") or "",
                "teaches": [ls["title"] for ls in ch["lessons"]],
            }
        )
    return parts


def write_category_stub():
    folder = os.path.join(ROOT, "category", "review")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "index.html")
    if os.path.exists(path):
        return
    body = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,follow">
  <title>レビュー一覧へ移動しました｜GOMIRACHELIN</title>
  <meta name="description" content="レビューの古いアドレスです。サウナ正直レビューの一覧へ移動します。">
  <meta http-equiv="refresh" content="0; url=/sauna-cospa/reviews/">
  <link rel="canonical" href="https://gomirachelin.github.io/sauna-cospa/reviews/">
  <link rel="stylesheet" href="/sauna-cospa/css/site.css">
</head>
<body>
<main class="page-main"><article class="entry"><header class="entry-head">
  <p class="kicker">MOVED</p>
  <h1>レビュー一覧</h1>
  <p>このアドレスは移動しました。</p>
  <p><a href="/sauna-cospa/reviews/">サウナ正直レビュー一覧を開く</a></p>
</header></article></main>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


def legacy_maps():
    urls = load_urls()
    by_id = {}
    for item in urls:
        slug = item.get("slug") or ""
        if slug == "top":
            dest = PREFIX + "/"
        else:
            dest = PREFIX + "/" + slug + "/"
        by_id[str(item.get("id"))] = dest
    by_slug = {}
    for path in iter_html():
        rel = rel_of(path)
        if rel.endswith("/index.html") and rel != "index.html":
            slug = rel[: -len("/index.html")]
            # category/review は転送なので、slug の最後だけでも拾う
            by_slug[slug] = PREFIX + "/" + slug + "/"
            by_slug[slug.split("/")[-1]] = PREFIX + "/" + slug + "/"
        elif rel == "sauna-daigaku.html":
            by_slug["sauna-daigaku.html"] = PREFIX + "/sauna-daigaku.html"
            by_slug["sauna-daigaku"] = PREFIX + "/sauna-daigaku.html"
    # 正式ページがある施設は、転送用フォルダより正式URLを優先する
    for item in urls:
        slug = item.get("slug") or ""
        if not slug or slug == "top":
            continue
        folder = os.path.join(ROOT, slug, "index.html")
        if os.path.exists(folder):
            by_slug[slug] = PREFIX + "/" + slug + "/"
    # 重複投稿の古いフォルダは、正式ページへ渡す
    by_slug["オアシスサウナ-アスティル-2"] = PREFIX + "/オアシスサウナ-アスティル/"
    by_slug["上野ステーションホステル-オリエンタル2-2"] = PREFIX + "/上野ステーションホステル-オリエンタル2/"
    aliases = {
        "/category/review": PREFIX + "/reviews/",
        "/category/reviews": PREFIX + "/reviews/",
        "/category/column": PREFIX + "/reviews/",
        "/review": PREFIX + "/reviews/",
        "/reviews": PREFIX + "/reviews/",
        "/ranking": PREFIX + "/ランキング/",
        "/rankings": PREFIX + "/ランキング/",
        "/contact": PREFIX + "/お問い合わせ/",
        "/about": PREFIX + "/運営者情報/",
        "/privacy": PREFIX + "/プライバシーポリシー/",
        "/disclaimer": PREFIX + "/免責事項/",
        "/university": PREFIX + "/sauna-university/",
        "/sauna-university": PREFIX + "/sauna-university/",
        "/how": PREFIX + "/how/",
        "/why": PREFIX + "/why/",
        "/map": PREFIX + "/map/",
        "/world": PREFIX + "/world/",
        "/sauna-daigaku": PREFIX + "/sauna-daigaku.html",
    }
    return by_id, by_slug, aliases


def js_object(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def inject_legacy_redirects(text, rel, by_id, by_slug, aliases):
    if rel == "index.html":
        script = (
            '<script id="legacy-query-redirect">\n'
            "(function(){\n"
            "  try {\n"
            "    var q = new URLSearchParams(location.search);\n"
            "    var id = q.get('page_id') || q.get('p');\n"
            f"    var map = {js_object(by_id)};\n"
            "    if (!id || !map[id]) return;\n"
            "    var dest = map[id];\n"
            "    var here = location.pathname.replace(/\\/+$/, '');\n"
            "    var there = dest.replace(/\\/+$/, '');\n"
            "    if (here === there) return;\n"
            "    if ((here === '/sauna-cospa' || here === '') && (there === '/sauna-cospa')) return;\n"
            "    location.replace(dest);\n"
            "  } catch (e) {}\n"
            "})();\n"
            "</script>\n"
        )
        text = re.sub(r'\s*<script id="legacy-query-redirect">.*?</script>\s*', "\n", text, flags=re.S)
        text = text.replace("</head>", script + "</head>", 1)
        return text
    if rel == "404.html":
        script = (
            '<script id="legacy-path-redirect">\n'
            "(function(){\n"
            "  try {\n"
            f"    var byId = {js_object(by_id)};\n"
            f"    var bySlug = {js_object(by_slug)};\n"
            f"    var aliases = {js_object(aliases)};\n"
            "    var q = new URLSearchParams(location.search);\n"
            "    var id = q.get('page_id') || q.get('p');\n"
            "    var dest = (id && byId[id]) ? byId[id] : '';\n"
            "    if (!dest) {\n"
            "      var path = location.pathname;\n"
            "      try { path = decodeURIComponent(path); } catch (e) {}\n"
            "      var prefix = '/sauna-cospa';\n"
            "      if (path.indexOf(prefix + '/') === 0) path = path.slice(prefix.length);\n"
            "      else if (path === prefix) path = '/';\n"
            "      path = path.replace(/\\/index\\.html$/, '').replace(/\\.html$/, '').replace(/\\/+$/, '') || '/';\n"
            "      if (aliases[path]) dest = aliases[path];\n"
            "      if (!dest) {\n"
            "        var m = path.match(/^\\/(?:\\d{4})(?:\\/\\d{1,2}){0,2}\\/(.+)$/);\n"
            "        if (m) path = '/' + m[1];\n"
            "        var seg = path.replace(/^\\//, '');\n"
            "        if (bySlug[seg]) dest = bySlug[seg];\n"
            "      }\n"
            "    }\n"
            "    if (!dest) return;\n"
            "    var here = location.pathname.replace(/\\/+$/, '');\n"
            "    var there = dest.replace(/\\/+$/, '');\n"
            "    if (here !== there) location.replace(dest);\n"
            "  } catch (e) {}\n"
            "})();\n"
            "</script>\n"
        )
        text = re.sub(r'\s*<script id="legacy-path-redirect">.*?</script>\s*', "\n", text, flags=re.S)
        text = text.replace("</head>", script + "</head>", 1)
    return text


def write_sitemap(rels):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for rel in rels:
        loc = canonical_from_rel(rel)
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(loc)}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    lines.append("")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def make_og_image():
    from PIL import Image, ImageDraw, ImageFont

    folder = os.path.join(ROOT, "assets", "images")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "og-default.png")
    img = Image.new("RGB", (1200, 630), "#0b0b0b")
    draw = ImageDraw.Draw(img)
    draw.rectangle((36, 36, 1164, 594), outline="#d4a017", width=3)
    draw.rectangle((48, 48, 1152, 52), fill="#d4a017")
    latin = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    latin_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 84)
    jp = ImageFont.truetype("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", 36)
    def center(text, font, y, fill):
        box = draw.textbbox((0, 0), text, font=font)
        w = box[2] - box[0]
        draw.text(((1200 - w) / 2, y), text, font=font, fill=fill)
    center("SAUNA COSPA GUIDE", latin, 150, "#d4a017")
    center("GOMIRACHELIN", latin_b, 220, "#f4d56b")
    center("コスパで選ぶ、全国サウナ正直ガイド", jp, 360, "#ece4d2")
    center("正直レビュー・ランキング・サウナ大学", jp, 450, "#c9c2b2")
    img.save(path, "PNG", optimize=True)
    return path


def check_links():
    from html.parser import HTMLParser
    from urllib.parse import unquote, urlparse

    class P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.refs = []
        def handle_starttag(self, tag, attrs):
            d = dict(attrs)
            if tag == "a" and d.get("href"):
                self.refs.append(d["href"])
            if tag in ("img", "script", "source", "video", "audio") and d.get("src"):
                self.refs.append(d["src"])
            if tag == "link" and d.get("href") and ("stylesheet" in (d.get("rel") or "") or d.get("rel") in ("icon", "apple-touch-icon", "manifest")):
                self.refs.append(d["href"])
            if tag == "meta" and (d.get("http-equiv") or "").lower() == "refresh":
                content = d.get("content") or ""
                m = re.search(r"url=([^;]+)", content, re.I)
                if m:
                    self.refs.append(m.group(1).strip())

    broken = []
    files = list(iter_html())
    for path in files:
        rel = rel_of(path)
        text = open(path, encoding="utf-8").read()
        parser = P()
        try:
            parser.feed(text)
        except Exception as e:
            broken.append((rel, "(parse)", str(e)))
            continue
        refs = list(parser.refs)
        refs += re.findall(r"url\((['\"]?)(/[^)'\"]+)\1\)", text)
        for href in refs:
            if isinstance(href, tuple):
                href = href[1]
            href = href.strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            if "${" in href or "\\" in href:
                broken.append((rel, href, "テンプレートか壊れた引用符"))
                continue
            if href.startswith("http://") or href.startswith("https://"):
                host = urlparse(href).netloc.lower()
                if host not in ("gomirachelin.github.io", "sauna-cospa.com", "www.sauna-cospa.com"):
                    continue
                url_path = unquote(urlparse(href).path)
            else:
                url_path = unquote(href.split("#", 1)[0].split("?", 1)[0])
                if not url_path.startswith("/"):
                    base = "/" + os.path.dirname(rel)
                    url_path = os.path.normpath(os.path.join(base if base != "/" else "/", url_path))
                    if not url_path.startswith("/"):
                        url_path = "/" + url_path
            if url_path.startswith(PREFIX + "/"):
                repo = url_path[len(PREFIX):]
            elif url_path == PREFIX:
                repo = "/"
            else:
                # このサイトの外（組織サイト直下など）は、ここにはファイルが無い
                broken.append((rel, href, " /sauna-cospa/ が付いていない: " + url_path))
                continue
            if repo in ("", "/"):
                fs = os.path.join(ROOT, "index.html")
            else:
                fs = os.path.join(ROOT, repo.lstrip("/"))
            ok = os.path.exists(fs)
            if not ok and repo.endswith("/"):
                ok = os.path.exists(os.path.join(ROOT, repo.strip("/") , "index.html"))
            if not ok and not repo.endswith("/"):
                ok = os.path.exists(os.path.join(fs, "index.html")) or os.path.exists(fs + ".html")
            if not ok:
                broken.append((rel, href, repo))
    return broken, len(files)


def main():
    global COURSE_PARTS
    print("共有画像を作ります")
    make_og_image()
    write_category_stub()
    print("サウナ大学の中身を取り出します")
    data = extract_course()
    if not data:
        raise SystemExit(1)
    COURSE_PARTS = course_parts_from(data)
    print(f"  章 {len(data['chapters'])} / 用語 {len(data['glossary'])} / クイズ {data['quiz']}")

    daigaku_path = os.path.join(ROOT, "sauna-daigaku.html")
    daigaku = open(daigaku_path, encoding="utf-8").read()
    daigaku = patch_daigaku(daigaku, data)
    open(daigaku_path, "w", encoding="utf-8").write(daigaku)

    manifest_path = os.path.join(ROOT, "sauna-app.webmanifest")
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    manifest["start_url"] = "/sauna-cospa/sauna-daigaku.html"
    manifest["scope"] = "/sauna-cospa/"
    manifest["icons"][0]["src"] = "/sauna-cospa/sauna-icon-180.png"
    json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(manifest_path, "a", encoding="utf-8").write("\n")

    dates = {}
    for item in load_urls():
        slug = item.get("slug")
        if not slug or slug == "top":
            continue
        day = (item.get("date") or "")[:10]
        dates[slug + "/index.html"] = day

    by_id, by_slug, aliases = legacy_maps()
    # category スタブを作ったあとで slug 表を取り直す
    by_id, by_slug, aliases = legacy_maps()

    changed = 0
    for path in sorted(iter_html()):
        rel = rel_of(path)
        text = open(path, encoding="utf-8").read()
        new = fix_world_links(fix_refresh(text))
        new = apply_document(new, rel, dates)
        new = inject_legacy_redirects(new, rel, by_id, by_slug, aliases)
        if new != text:
            open(path, "w", encoding="utf-8").write(new)
            changed += 1
    print(f"HTMLを更新: {changed} ファイル")

    rels = []
    for path in sorted(iter_html()):
        rel = rel_of(path)
        text = open(path, encoding="utf-8").read()
        if rel in SITEMAP_SKIP or is_noindex(text):
            continue
        rels.append(rel)
    write_sitemap(rels)
    print(f"sitemap: {len(rels)} URL")

    broken, nfiles = check_links()
    print(f"リンク検査: {nfiles} ファイル / 壊れ {len(broken)}")
    for row in broken[:80]:
        print(" ", row)
    if len(broken) > 80:
        print(f"  ... 他 {len(broken) - 80} 件")
    return broken


if __name__ == "__main__":
    main()
