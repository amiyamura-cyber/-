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
# 2. サイドバーの設定（優先順位順に配置）
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
# 🔍 1. SEO対策アプリ
# ------------------------------------------
if page == "🔍 1. SEO対策アプリ":
    # 記憶エリアの初期化
    if "used_keywords" not in st.session_state: st.session_state.used_keywords = []
    if "search_clicked" not in st.session_state: st.session_state.search_clicked = False
    if "cur_grouped_keywords" not in st.session_state: st.session_state.cur_grouped_keywords = []
    if "cur_articles" not in st.session_state: st.session_state.cur_articles = []

    st.markdown("""
    <style>
        .hero-container { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); padding: 35px 30px; border-radius: 16px; color: white; margin-bottom: 30px; }
        .hero-title { font-size: 2.2rem !important; font-weight: 700 !important; color: #f3f4f6; }
        .group-box { background-color: #1f2937; padding: 20px 15px; border-radius: 14px; text-align: center; margin-bottom: 12px; }
        .group-title { color: #3b82f6; font-weight: 700; font-size: 1.1rem; margin-bottom: 15px; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; }
        .seo-mini-badge { background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%); color: white; padding: 14px 12px; border-radius: 8px; font-weight: 700; font-size: 0.95rem; }
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
        st.rerun()

    if st.session_state.used_keywords:
        for uw in st.session_state.used_keywords:
            st.sidebar.markdown(f"- **{uw}** `(除外)`")

    if search_trigger:
        if not keyword:
            st.error("⚠️ 検索キーワードを入力してください。")
        else:
            clean_keyword = re.sub(r'\s+', ' ', keyword).strip()
            
            # ダミーデータとシャッフル（※元の処理をそのまま維持）
            seo_pool = ["戦略", "計画", "分析", "効果", "最適", "効率", "組織", "育成", "定着", "マッチング", "コスト", "プロセス", "フロー", "評価", "基準"]
            random.shuffle(seo_pool)
            st.session_state.cur_grouped_keywords = [seo_pool[i*3 : (i+1)*3] for i in range(5)]
            st.session_state.search_clicked = True

    if not st.session_state.search_clicked:
        st.info("左側のサイドバーから検索キーワードを入力し、ボタンを押してください。")
    else:
        st.success("🎉 分析が完了しました！")
        st.markdown(f"### 🎯 「{keyword}」の掛け合わせSEOキーワード")
        group_cols = st.columns(5)
        for i, group in enumerate(st.session_state.cur_grouped_keywords):
            with group_cols[i]:
                st.markdown(f'<div class="group-box"><div class="group-title">📦 グループ {i+1}</div><div class="seo-mini-badge">{" ・ ".join(group)}</div></div>', unsafe_allow_html=True)
        
        lines = [f"【グループ{i+1}】 " + " ".join(group) for i, group in enumerate(st.session_state.cur_grouped_keywords)]
        st.text_area(label="📋 コピペ用テキスト", value="\n".join(lines), height=150)

        # ---------------------------------------------------------
        # ▼ 送っていただいた「司令塔（ポータル）機能」のリンクを追加
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
            # ※URLは後で設定します
            st.link_button("📝 管理画面（CMS）を開く ↗", "https://your-cms-url.com", use_container_width=True, type="primary")

# ------------------------------------------
# 📝 2. 管理画面へ移動 (ジャンプリンク)
# ------------------------------------------
elif page == "📝 2. 管理画面へ移動":
    st.markdown("### 📝 管理画面（CMS）へ移動")
    st.write("以下のボタンをクリックして、別タブで記事の入稿・管理画面を開いてください。")
    # ※URLは後で設定します
    st.link_button("📝 管理画面を開く ↗", "https://your-cms-url.com", use_container_width=True, type="primary")

# ------------------------------------------
# 🤖 3. 対話ボット (自動プロンプト生成)
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
# 🌐 4. 比較サイトへ移動 (ジャンプリンク)
# ------------------------------------------
elif page == "🌐 4. 比較サイトへ移動":
    st.markdown("### 🌐 比較サイトの確認")
    st.write("以下のボタンをクリックして、実際の比較サイト（表側）を確認してください。")
    # ※URLは後で設定します
    st.link_button("🌐 比較サイトを開く ↗", "https://your-site-url.com", use_container_width=True)
