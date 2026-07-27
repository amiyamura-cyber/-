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
    initial_sidebar_state="collapsed" # サイドバーは最初から閉じておく
)

# 記憶エリアの初期化
if "used_keywords" not in st.session_state: st.session_state.used_keywords = []
if "search_clicked" not in st.session_state: st.session_state.search_clicked = False
if "cur_grouped_keywords" not in st.session_state: st.session_state.cur_grouped_keywords = []
if "cur_articles" not in st.session_state: st.session_state.cur_articles = []

# カスタムCSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans JP', sans-serif; }
    .hero-container { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); padding: 30px 30px; border-radius: 12px; color: white; margin-bottom: 20px; text-align: center;}
    .hero-title { font-size: 2rem !important; font-weight: 700 !important; color: #f3f4f6; margin:0;}
    .group-box { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; text-align: center; margin-bottom: 10px; }
    .group-title { color: #3b82f6; font-weight: 700; font-size: 1rem; margin-bottom: 10px; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; }
    .seo-mini-badge { background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%); color: white; padding: 10px; border-radius: 6px; font-weight: 700; font-size: 0.9rem; word-break: break-all; }
    .article-card { background: #111827; border: 1px solid #374151; border-radius: 10px; padding: 20px; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    .article-title { font-size: 1.1rem; font-weight: 700; color: #f3f4f6; margin-bottom: 10px; }
    .article-summary { font-size: 0.85rem; color: #9ca3af; margin-bottom: 15px; flex-grow: 1; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-container"><h1 class="hero-title">🚀 エアログ統合システム（記事作成ポータル）</h1></div>', unsafe_allow_html=True)

# ==========================================
# 2. 横タブの作成（ここで1枚のページを分割）
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 1. SEOキーワード抽出", 
    "🤖 2. 対話ボット(プロンプト)", 
    "📝 3. 管理画面へ", 
    "🌐 4. サイト確認"
])

# ------------------------------------------
# タブ1: SEO対策アプリ
# ------------------------------------------
with tab1:
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("### 🔍 検索条件")
        keyword = st.text_input("検索キーワード", value="採用 企業向け")
        search_trigger = st.button("🎲 抽出を実行", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📋 記憶したキーワード")
        if st.button("🗑️ リセット", use_container_width=True):
            st.session_state.used_keywords = []
            st.session_state.search_clicked = False
            st.rerun()
            
        if st.session_state.used_keywords:
            for uw in st.session_state.used_keywords:
                st.markdown(f"- **{uw}** `(除外)`")
        else:
            st.caption("記憶なし")

    with col_right:
        if search_trigger:
            if not keyword:
                st.error("⚠️ キーワードを入力してください。")
            else:
                # --- 抽出処理（短縮） ---
                clean_keyword = re.sub(r'\s+', ' ', keyword).strip()
                seo_pool = ["戦略", "計画", "分析", "効果", "最適", "効率", "組織", "育成", "定着", "マッチング", "コスト", "プロセス", "フロー", "評価", "基準"]
                random.shuffle(seo_pool)
                st.session_state.cur_grouped_keywords = [seo_pool[i*3 : (i+1)*3] for i in range(5)]
                
                # ダミー記事データ
                st.session_state.cur_articles = [
                    {"title": f"【最新】{clean_keyword}の成功事例", "summary": "最新のトレンドを解説します。", "url": "https://example.com"},
                    {"title": f"{clean_keyword}で失敗しないためのポイント", "summary": "初心者が陥りがちなミスと対策。", "url": "https://example.com"}
                ]
                st.session_state.search_clicked = True

        if not st.session_state.search_clicked:
            st.info("👈 左側のパネルから検索キーワードを入力し、抽出ボタンを押してください。")
        else:
            st.success("🎉 分析が完了しました！結果をもとに「タブ2」へ進んでください。")
            st.markdown(f"#### 🎯 「{keyword}」のSEOキーワード")
            
            group_cols = st.columns(5)
            for i, group in enumerate(st.session_state.cur_grouped_keywords):
                with group_cols[i]:
                    st.markdown(f'<div class="group-box"><div class="group-title">グループ {i+1}</div><div class="seo-mini-badge">{" ・ ".join(group)}</div></div>', unsafe_allow_html=True)
            
            lines = [f"【グループ{i+1}】 " + " ".join(group) for i, group in enumerate(st.session_state.cur_grouped_keywords)]
            st.text_area(label="📋 コピペ用テキスト", value="\n".join(lines), height=120)

# ------------------------------------------
# タブ2: AI対話ボット
# ------------------------------------------
with tab2:
    st.markdown("### 🤖 記事作成 AIアシスタント")
    with st.chat_message("assistant"):
        st.write("タブ1で抽出したキーワードなどを使って、以下の**【3つの条件】**を教えてください。")

    with st.form("prompt_form"):
        kw = st.text_input("1. 対策キーワード", placeholder="例：採用 企業向け")
        target = st.text_area("2. 記事の内容やターゲット", placeholder="例：採用に困っている中小企業の人事担当者向け。")
        words = st.text_input("3. 文字数の目安", placeholder="例：10000文字程度")
        submitted = st.form_submit_button("✨ プロンプト（指示書）を生成する", type="primary")

    if submitted:
        if not kw or not target or not words:
            st.error("3つの条件をすべて入力してください！")
        else:
            prompt_text = f"""あなたはプロのSEOコンサルタント兼凄腕Webライターです。
以下の【3つの条件】をもとに、検索上位を狙えるSEO記事を作成してください。
1. 対策キーワード: {kw}
2. 記事の内容やターゲット: {target}
3. 文字数の目安: {words}
(※以下、フォーマット指示が続きます...)""" # ←実際には元の長いプロンプトが入ります

            st.success("✅ 指示書が完成しました！コピーしてAIに貼り付け、記事ができたら「タブ3」へ進んでください。")
            st.code(prompt_text, language="text")
            
            col1, col2 = st.columns(2)
            with col1:
                st.link_button("🤖 Gemini を開く ↗", "https://gemini.google.com/app", use_container_width=True)
            with col2:
                st.link_button("🤖 ChatGPT を開く ↗", "https://chatgpt.com/", use_container_width=True)

# ------------------------------------------
# タブ3: 管理画面へ
# ------------------------------------------
with tab3:
    st.markdown("### 📝 管理画面（CMS）へのアクセス")
    st.write("AIが作成したHTMLコードをコピーしたら、以下のボタンから管理画面を開いて貼り付け、公開してください。")
    st.link_button("📝 管理画面を開く ↗", "https://amiyamura-cyber.github.io/air-log-site/admin.html", use_container_width=True, type="primary")

# ------------------------------------------
# タブ4: 比較サイト確認
# ------------------------------------------
with tab4:
    st.markdown("### 🌐 比較サイトの確認")
    st.write("記事を公開したら、以下のボタンから実際のサイトを確認してみましょう！")
    st.link_button("🌐 比較サイトを開く ↗", "https://amiyamura-cyber.github.io/air-log-site/", use_container_width=True)
