import streamlit as st
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import random
import html

# ==========================================
# 1. ページ全体の設定
# ==========================================
st.set_page_config(
    page_title="エアログ統合システム",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. サイドバーの設定（メニュー）
# ==========================================
st.sidebar.markdown("## ⚙️ エアログ統合メニュー")
page = st.sidebar.radio(
    "機能を選択してください",
    [
        "🔍 1. SEO対策アプリ", 
        "📝 2. 管理画面へ移動", 
        "🤖 3. 対話ボット", 
        "🌐 4. 比較サイトへ移動"
    ]
)
st.sidebar.markdown("---")

# ==========================================
# 3. 各画面の処理
# ==========================================

# ------------------------------------------
# 🔍 1. SEO対策アプリ（完全版）
# ------------------------------------------
if page == "🔍 1. SEO対策アプリ":
    # 記憶エリアの初期化
    if "used_keywords" not in st.session_state:
        st.session_state.used_keywords = []
    if "search_clicked" not in st.session_state:
        st.session_state.search_clicked = False
    if "cur_grouped_keywords" not in st.session_state:
        st.session_state.cur_grouped_keywords = []
    if "cur_articles" not in st.session_state:
        st.session_state.cur_articles = []

    # カスタムCSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto Sans JP', sans-serif; }
        .hero-container { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); padding: 35px 30px; border-radius: 16px; color: white; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); border: 1px solid #374151; }
        .hero-title { font-size: 2.2rem !important; font-weight: 700 !important; color: #f3f4f6; }
        .group-box { background-color: #1f2937; padding: 20px 15px; border-radius: 14px; border: 1px solid #374151; box-shadow: 0 4px 12px rgba(0,0,0,0.15); text-align: center; margin-bottom: 12px; }
        .group-title { color: #3b82f6; font-weight: 700; font-size: 1.1rem; margin-bottom: 15px; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; }
        .seo-mini-badge { background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%); color: white; padding: 14px 12px; border-radius: 8px; font-weight: 700; font-size: 0.95rem; box-shadow: 0 3px 6px rgba(79, 70, 229, 0.2); border: 1px solid rgba(255,255,255,0.1); word-break: break-all; line-height: 1.5; display: block; }
        .article-card { background: #111827; border: 1px solid #374151; border-radius: 14px; padding: 24px; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 15px rgba(0,0,0,0.15); transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
        .article-title { font-size: 1.15rem; font-weight: 700; color: #f3f4f6; margin-bottom: 12px; line-height: 1.4; }
        .article-summary { font-size: 0.9rem; color: #9ca3af; line-height: 1.6; margin-bottom: 20px; flex-grow: 1; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hero-container"><div class="hero-title">📈 無限記事＆SEOグループナビゲーター</div></div>', unsafe_allow_html=True)

    st.sidebar.markdown("### 🔍 検索条件の設定")
    keyword = st.sidebar.text_input("検索キーワード", value="採用 企業向け")
    search_trigger = st.sidebar.button("🎲 記事＆SEOグループを抽出（連打OK）", type="primary", use_container_width=True)
    st.sidebar.markdown("---")

    st.sidebar.markdown("### 📋 記憶したキーワード一覧")
    if st.sidebar.button("🗑️ 記憶をすべてリセット", use_container_width=True):
        st.session_state.used_keywords = []
        st.session_state.search_clicked = False
        st.success("記憶をリセットしました！")
        st.rerun()

    if st.session_state.used_keywords:
        for uw in st.session_state.used_keywords:
            st.sidebar.markdown(f"- **{uw}** `(次回以降100%除外)`")
    else:
        st.sidebar.caption("まだ記憶されたキーワードはありません。")

    if search_trigger:
        if not keyword:
            st.error("⚠️ 検索キーワードを入力してください。")
        else:
            clean_keyword = re.sub(r'\s+', ' ', keyword).strip()
            query_modifiers = ["", "事例", "ノウハウ", "課題", "実務", "最前線", "戦略", "手法"]
            chosen_modifiers = random.sample(query_modifiers, 4)
            
            raw_pool = []
            for mod in chosen_modifiers:
                target_query = f"{clean_keyword} {mod}".strip()
                try:
                    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(target_query)}&hl=ja&gl=JP&ceid=JP:ja"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=4) as response:
                        root = ET.fromstring(response.read())
                        for item in root.findall('.//item')[:30]:
                            t = item.find('title').text or ""
                            u = item.find('link').text or ""
                            d = item.find('description').text if item.find('description') is not None else ""
                            if " - " in t: t = " - ".join(t.split(" - ")[:-1])
                            d = re.sub(r'<[^>]+>', '', d)
                            d = html.unescape(d).strip() if d else ""
                            if len(d) > 100: d = d[:100] + "..."
                            if not d: d = "最新の人材採用関連ニュース・解説記事です。"
                            raw_pool.append({"title": t, "url": u, "summary": d})
                except Exception:
                    pass

            random.shuffle(raw_pool)

            backup_pool = [
                {"title": "【新卒採用】2027年卒新卒採用動向とインターンシップの新ルール（マイナビ）", "summary": "企業・学生双方からの評価が最も高い新卒の定番。最新選考ルールやスケジュール設計を網羅。", "url": "https://job.mynavi.jp/conts/2027/"},
                {"title": "【中途採用】即戦力を獲得するダイレクトリクルーティング成功の教科書（ビズリーチ）", "summary": "人事担当者から絶大な支持を得ている中途決定版。スカウト返信率を引き上げる具体的な文面ノウハウ。", "url": "https://bizreach.biz/service/direct-recruiting/"},
                {"title": "【離職防止】早期離職を防ぐための採用ブランディングとマッチング事例（HRプロ）", "summary": "自社のリアルな社風を正しく発信し、カルチャーにマッチした人材を呼び込む特化記事。", "url": "https://www.hrpro.co.jp/branding_case/"},
                {"title": "【シニア雇用】労働力不足を救うシニア人材・高齢者活用の現場課題と対策（日経ビジネス）", "summary": "深刻な人手不足への対策として評判が非常に高い特集。シニア層の人事評価や賃金設計を解説。", "url": "https://www.nikkei.com/business/hr/"},
                {"title": "【求人法律】求人票の労働条件明示変更！人事担当者が今すぐやるべき法律対策（厚生労働省）", "summary": "全企業が確認すべき最重要の公式法律コンテンツ。求人票の記載ルールやトラブル回避策を網羅。", "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/koyou/shokuhaku/index.html"}
            ]
            random.shuffle(backup_pool)

            clean_articles = []
            seen_domains = set()
            ban_words = ["openai", "open ai", "オープンai", "claude", "chatgpt", "生成ai", "エージェント", "新会社", "設立", "省エネ"]
            ignore_words = {"最新", "方法", "解説", "まとめ", "とは", "成功", "ノウハウ", "企業", "向け", "ポイント", "事例", "動向", "現状", "課題", "対策", "採用", "人事", "徹底", "戦略"}

            for sw in re.findall(r'[\u4e00-\u9fff\u30a0-\u30ff\w]+', clean_keyword.lower()):
                ignore_words.add(sw)

            for art in raw_pool:
                if len(clean_articles) >= 10: break
                t = art["title"]
                t_lower = t.lower()
                u = art["url"]
                
                if any(bw in t_lower for bw in ban_words): continue
                if any(uw.lower() in t_lower for uw in st.session_state.used_keywords): continue
                    
                domain_match = re.search(r'https?://([^/]+)', u)
                domain = domain_match.group(1) if domain_match else u
                if domain in seen_domains: continue
                
                clean_articles.append(art)
                seen_domains.add(domain)

            for bk in backup_pool:
                if len(clean_articles) >= 10: break
                if bk not in clean_articles:
                    if not any(uw.lower() in bk["title"].lower() for uw in st.session_state.used_keywords):
                        clean_articles.append(bk)

            st.session_state.cur_articles = clean_articles[:10]

            hints_pool = ["あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ", "さ", "し", "す", "せ", "そ", "課題", "対策", "事例", "転職", "比較", "最新"]
            chosen_hints = random.sample(hints_pool, 5)
            raw_candidates = []
            for hint in [""] + chosen_hints:
                search_query = f"{clean_keyword} {hint}".strip()
                suggest_url = f"http://suggestqueries.google.com/complete/search?output=toolbar&hl=ja&q={urllib.parse.quote(search_query)}"
                suggest_req = urllib.request.Request(suggest_url, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    with urllib.request.urlopen(suggest_req, timeout=3) as sug_response:
                        sug_root = ET.fromstring(sug_response.read())
                        for item in sug_root.findall('.//suggestion'):
                            w_val = item.get('data')
                            if w_val and w_val.strip() not in raw_candidates: 
                                raw_candidates.append(w_val.strip())
                except Exception:
                    pass
            
            seo_pool = []
            for cand in raw_candidates:
                remainder = cand.replace(clean_keyword, "").strip()
                if not remainder or remainder == clean_keyword: continue
                pure_words = re.findall(r'[\u4e00-\u9fff]{2,}|[\u30a0-\u30ff]{2,}|[a-zA-Z0-9]{2,}', remainder)
                for w in pure_words:
                    if w in ignore_words or len(w) < 2: continue
                    if w in st.session_state.used_keywords: continue
                    if not any(w in s or s in w for s in seo_pool) and w not in seo_pool:
                        seo_pool.append(w)
            
            random.shuffle(seo_pool)
            
            huge_fallback_pool = [
                "戦略", "計画", "分析", "効果", "最適", "効率", "組織", "育成", "定着", "マッチング",
                "コスト", "プロセス", "フロー", "評価", "基準", "面接", "内定", "辞退", "フォロー", "研修"
            ]
            random.shuffle(huge_fallback_pool)
            
            for word in huge_fallback_pool:
                if len(seo_pool) >= 15: break
                if word not in seo_pool and word not in st.session_state.used_keywords:
                    seo_pool.append(word)
                    
            while len(seo_pool) < 15:
                seo_pool.append(f"単語{len(seo_pool)+1}")
            
            seo_keywords = seo_pool[:15]
            st.session_state.cur_grouped_keywords = [seo_keywords[i*3 : (i+1)*3] for i in range(5)]
            st.session_state.search_clicked = True

    if not st.session_state.search_clicked:
        st.markdown("""
        <div style="background-color: #1f2937; padding: 40px; border-left: 6px solid #3b82f6; border-radius: 12px; border: 1px solid #374151;">
            <h3 style="color: #ffffff; margin-bottom: 15px; font-weight: 700;">👋 ご利用方法</h3>
            <p style="color: #9ca3af; font-size: 1.05rem;">左側のサイドバーにキーワードを入力し、ボタンを押してください。</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("🎉 分析が完了しました！")
        st.markdown(f"### 🎯 「{keyword}」の掛け合わせSEOキーワード（単語3語×5グループ）")

        sel_col1, sel_col2, _ = st.columns([1.5, 1.5, 7])
        with sel_col1:
            if st.button("✅ すべてチェック", use_container_width=True):
                for idx, group in enumerate(st.session_state.cur_grouped_keywords):
                    for word in group:
                        st.session_state[f"chk_{word}_{idx}"] = True
                st.rerun()
        with sel_col2:
            if st.button("❌ チェックを外す", use_container_width=True):
                for idx, group in enumerate(st.session_state.cur_grouped_keywords):
                    for word in group:
                        st.session_state[f"chk_{word}_{idx}"] = False
                st.rerun()

        st.write("")
        selected_to_register = []
        group_cols = st.columns(5)
        
        for i, group in enumerate(st.session_state.cur_grouped_keywords):
            with group_cols[i]:
                st.markdown(f"""
                <div class="group-box">
                    <div class="group-title">📦 グループ {i+1}</div>
                    <div class="seo-mini-badge">{" ・ ".join(group)}</div>
                </div>
                """, unsafe_allow_html=True)
                
                for word in group:
                    if word in st.session_state.used_keywords:
                        st.caption(f"🔒 {word} (記憶済み)")
                    else:
                        if st.checkbox(f"使用した: {word}", key=f"chk_{word}_{i}"):
                            selected_to_register.append(word)

        if selected_to_register:
            st.write("")
            if st.button("📥 選択したキーワードを記憶する（次回除外）", type="primary", use_container_width=True):
                for w in selected_to_register:
                    if w not in st.session_state.used_keywords:
                        st.session_state.used_keywords.append(w)
                st.success("使用済みキーワードとして記憶しました！")
                st.rerun()

        lines = [f"【グループ{i+1}】 " + " ".join(group) for i, group in enumerate(st.session_state.cur_grouped_keywords)]
        keywords_text = "\n".join(lines)
        st.write("")
        st.text_area(label="📋 コピペ用テキストエリア", value=keywords_text, height=150)
        
        st.write("---")
        st.markdown("### 📰 関連する注目記事（重複・記憶ワード完全排除）")
        art_cols = st.columns(2) 
        for i, art in enumerate(st.session_state.cur_articles):
            with art_cols[i % 2]:
                st.markdown(f'<div class="article-card"><div><span class="article-index">注目記事 {i+1}</span><div class="article-title">{art.get("title")}</div><div class="article-summary">{art.get("summary")}</div></div></div>', unsafe_allow_html=True)
                st.link_button(f"記事をウェブで開く ↗️", art.get('url'), use_container_width=True)
                st.write("")

        # ---------------------------------------------------------
        # ▼ 司令塔（ポータル）機能：次のステップへの導線
        # ---------------------------------------------------------
        st.markdown("---")
        st.markdown("### 🚀 次のステップ（記事作成 〜 サイトへの投稿）")
        st.info("上のテキストエリアからキーワードをコピーしたら、以下の順番で作業を進めてください。")
        
        col_ai, col_cms = st.columns(2)
        
        with col_ai:
            st.markdown("#### STEP 2: AIに記事を書かせる")
            st.write("左のメニューから「🤖 3. 対話ボット」を選ぶか、下のボタンからAIを開きます。")
            st.link_button("🤖 Gemini を開く ↗", "https://gemini.google.com/app", use_container_width=True)
            
        with col_cms:
            st.markdown("#### STEP 3: サイトに投稿する")
            st.write("AIが作成したHTMLコードをコピーし、管理画面に貼り付けて公開します。")
            st.link_button("📝 管理画面（CMS）を開く ↗", "https://amiyamura-cyber.github.io/air-log-site/admin.html", use_container_width=True, type="primary")

# ------------------------------------------
# 📝 2. 管理画面へ移動
# ------------------------------------------
elif page == "📝 2. 管理画面へ移動":
    st.markdown("### 📝 管理画面（CMS）へ移動")
    st.write("以下のボタンをクリックして、別タブで記事の入稿・管理画面を開いてください。")
    st.link_button("📝 管理画面を開く ↗", "https://amiyamura-cyber.github.io/air-log-site/admin.html", use_container_width=True, type="primary")

# ------------------------------------------
# 🤖 3. 対話ボット (プロンプト自動生成)
# ------------------------------------------
elif page == "🤖 3. 対話ボット":
    st.markdown("### 🤖 記事作成 AIアシスタント")
    
    with st.chat_message("assistant"):
        st.write("プロのSEOコンサルタント兼凄腕Webライターです！検索上位を狙えるSEO記事を作成します。まずは以下の**【3つの条件】**を教えてください。")

    with st.form("prompt_form"):
        kw = st.text_input("1. 対策キーワード", placeholder="例：採用 企業向け")
        target = st.text_area("2. 記事の内容やターゲット", placeholder="例：採用に困っている中小企業の人事担当者向け。課題解決のノウハウを書きたい。")
        words = st.text_input("3. 文字数の目安", placeholder="例：10000文字程度")
        submitted = st.form_submit_button("✨ この条件で指示書（プロンプト）を生成する", type="primary")

    if submitted:
        if not kw or not target or not words:
            st.error("3つの条件をすべて入力してください！")
        else:
            prompt_text = f"""あなたはプロのSEOコンサルタント兼凄腕Webライターです。
以下の【3つの条件】をもとに、検索上位を狙えるSEO記事を作成してください。

1. 対策キーワード: {kw}
2. 記事の内容やターゲット: {target}
3. 文字数の目安: {words}

なお、記事を出力する際は、私がコピーしやすいように全体をコードブロック（```html ～ ```）で囲み、以下の【必ず守るべきHTMLフォーマットのルール】を厳格に守って出力してください。指定文字数に近づけるよう、見出しを十分に増やし、各項目を極限まで詳細に深掘りして記述してください。

【必ず守るべきHTMLフォーマットのルール】
すべての内容は以下のブロック形式で作成してください。独自のタグ（<section>など）や余計な説明文、および画像タグ（<img>）は絶対に含めず、純粋なHTMLコードのみを生成してください。

1. 導入文（リード文）
<!-- parts start -->
<div class="p-media-parts">
<p class="p-media-parts__txt">（ここに導入文を記述。改行する場合は<br /><br />を使用）</p>
</div>
<!-- parts end -->

2. 目次（TOC）
<!-- parts start -->
<div class="p-media-parts">
<div class="p-media-parts__toc">
<div class="p-media-parts__toc-inside">
<p class="h2">目次</p>
<ol class="p-media-parts__toc-list js-pagelink">
<li class="p-media-parts__toc-list__item"><a href="#a-01">（見出し2のタイトル）</a></li>
</ol>
</div>
</div>
</div>
<!-- parts end -->

3. 大見出し（H2）とその本文
<!-- parts start -->
<div id="a-01" class="p-media-parts mt-lg">
<h2 class="p-media-parts__h2">（見出し2のタイトル）</h2>
<p class="p-media-parts__txt">（本文を記述。改行する場合は<br /><br />を使用）</p>
</div>
<!-- parts end -->
※ id="a-01" の部分は見出しごとに a-02, a-03... と連番にしてください。

4. 小見出し（H3）とその本文
<!-- parts start -->
<div class="p-media-parts">
<h3 class="p-media-parts__h3">（見出し3のタイトル）</h3>
<p class="p-media-parts__txt">（本文を記述。改行する場合は<br /><br />を使用）</p>
</div>
<!-- parts end -->

5. 最後のまとめ部分
<!-- parts start -->
<div id="a-99" class="p-media-parts mt-lg">
<h2 class="p-media-parts__h2">まとめ</h2>
<p class="p-media-parts__txt">（まとめの本文を記述）</p>
</div>
<!-- parts end -->

【記事完成後の処理】
コードブロックでのHTML記事出力が終わったら、その下に通常のテキストで、SEO効果が高くクリック率が見込める魅力的な記事のタイトルを【1案のみ】提案してください。"""

            st.success("✅ 指示書が完成しました！右上のコピーボタンからコピーして、AIに貼り付けてください。")
            st.code(prompt_text, language="text")
            col1, col2 = st.columns(2)
            with col1:
                st.link_button("🤖 ChatGPT を開く ↗", "https://chatgpt.com/", use_container_width=True)
            with col2:
                st.link_button("🤖 Gemini を開く ↗", "https://gemini.google.com/app", use_container_width=True)

# ------------------------------------------
# 🌐 4. 比較サイトへ移動
# ------------------------------------------
elif page == "🌐 4. 比較サイトへ移動":
    st.markdown("### 🌐 比較サイトの確認")
    st.write("以下のボタンをクリックして、実際の比較サイト（表側）を確認してください。")
    st.link_button("🌐 比較サイトを開く ↗", "https://amiyamura-cyber.github.io/air-log-site/", use_container_width=True)
