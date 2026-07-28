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
    .article-index { font-size: 0.8rem; color: #3b82f6; font-weight: bold; margin-bottom: 5px; display: block; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-container"><h1 class="hero-title">🚀 エアログ統合システム（記事作成ポータル）</h1></div>', unsafe_allow_html=True)

# ==========================================
# 2. 横タブの作成
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "🔍 1. SEOキーワード抽出", 
    "📝 2. 管理画面へ", 
    "🌐 3. サイト確認"
])

# ------------------------------------------
# タブ1: SEO対策アプリ
# ------------------------------------------
with tab1:
    col_left, col_right = st.columns([1, 2.5])
    
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
                with st.spinner("情報を収集中..."):
                    clean_keyword = re.sub(r'\s+', ' ', keyword).strip()
                    
                    # --- 1. 記事の抽出処理 ---
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
                        {"title": "【求人法律】求人票の労働条件明示変更！人事担当者が今すぐやるべき法律対策（厚生労働省）", "summary": "全企業が確認すべき最重要の公式法律コンテンツ。求人票の記載ルールやトラブル回避策を網羅。", "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/koyou/shokuhaku/index.html"},
                        {"title": "【面接手法】優秀な人材を見抜く構造化面接のやり方と評価シート導入法", "summary": "面接官のスキルに頼らず、一貫した基準で応募者の能力を正確に見極めるための実践ガイドです。", "url": "https://doda.jp/biz/hint/knowhow/"},
                        {"title": "【求人媒体】主要な求人サイト・採用メディアの特徴とコスト徹底比較", "summary": "ターゲット層に合わせた最適な求人媒体の選び方と、求人広告のCRAを下げるコツ。", "url": "https://hrmos.co/media/"},
                        {"title": "【内定辞退】優秀な学生・求職者を逃さない内定者フォローの具体策", "summary": "内定者フォローのエンゲージメントを高めて辞退率を劇的に下げる実践テクニック。", "url": "https://www.wantedly.com/about/business"},
                        {"title": "【地方採用】ローカル中小企業が苦境を乗り越えるUIJターン獲得戦略", "summary": "地方への移住・転職希望者を惹きつける魅力的な求人設計と成功事例。", "url": "https://www.r-agent.com/business/"},
                        {"title": "【女性活躍】女性管理職・リーダーを育成する採用方針と人事制度改革", "summary": "キャリア志向の女性人材を惹きつけ、定着させるための柔軟な働き方制度と採用PRの手法。", "url": "https://women-type.jp/b/contents/"}
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

                    # --- 2. サジェストキーワード抽出処理 ---
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
                        "コスト", "プロセス", "フロー", "評価", "基準", "面接", "内定", "辞退", "フォロー", "研修",
                        "適性", "スキル", "経験", "キャリア", "求人", "媒体", "エージェント", "ダイレクト", "スカウト", "返信",
                        "エンゲージメント", "リファラル", "マネジメント", "リーダー", "即戦力", "ポテンシャル", "選考", "スケジュール"
                    ]
                    random.shuffle(huge_fallback_pool)
                    
                    for word in huge_fallback_pool:
                        if len(seo_pool) >= 15: break
                        if word not in seo_pool and word not in st.session_state.used_keywords:
                            seo_pool.append(word)
                            
                    if len(seo_pool) < 15:
                        for word in huge_fallback_pool:
                            if len(seo_pool) >= 15: break
                            if word not in seo_pool: seo_pool.append(word)
                                
                    while len(seo_pool) < 15:
                        seo_pool.append(f"単語{len(seo_pool)+1}")
                    
                    seo_keywords = seo_pool[:15]
                    st.session_state.cur_grouped_keywords = [seo_keywords[i*3 : (i+1)*3] for i in range(5)]
                    st.session_state.search_clicked = True

        if not st.session_state.search_clicked:
            st.info("👈 左側のパネルから検索キーワードを入力し、抽出ボタンを押してください。")
        else:
            st.success("🎉 分析が完了しました！抽出されたキーワードを使って記事を作成しましょう。")
            st.markdown(f"#### 🎯 「{keyword}」のSEOキーワード")
            
            group_cols = st.columns(5)
            for i, group in enumerate(st.session_state.cur_grouped_keywords):
                with group_cols[i]:
                    st.markdown(f'<div class="group-box"><div class="group-title">グループ {i+1}</div><div class="seo-mini-badge">{" ・ ".join(group)}</div></div>', unsafe_allow_html=True)
            
            lines = [f"【グループ{i+1}】 " + " ".join(group) for i, group in enumerate(st.session_state.cur_grouped_keywords)]
            st.text_area(label="📋 コピペ用テキスト", value="\n".join(lines), height=120)
            
            st.write("---")
            st.markdown("### 📰 関連する注目記事（最大10選）")
            art_cols = st.columns(2) 
            for i, art in enumerate(st.session_state.cur_articles):
                with art_cols[i % 2]:
                    st.markdown(f'<div class="article-card"><div><span class="article-index">注目記事 {i+1}</span><div class="article-title">{art.get("title")}</div><div class="article-summary">{art.get("summary")}</div></div></div>', unsafe_allow_html=True)
                    st.link_button(f"記事をウェブで開く ↗️", art.get('url'), use_container_width=True)
                    st.write("")

# ------------------------------------------
# タブ2: 管理画面へ
# ------------------------------------------
with tab2:
    st.markdown("### 📝 管理画面（CMS）へのアクセス")
    st.write("キーワード抽出が終わったら、以下のボタンから管理画面を開き、AIアシスタント機能を使って記事を作成・公開してください。")
    st.link_button("📝 管理画面を開く ↗", "https://amiyamura-cyber.github.io/air-log-site/admin.html", use_container_width=True, type="primary")

# ------------------------------------------
# タブ3: 比較サイト確認
# ------------------------------------------
with tab3:
    st.markdown("### 🌐 比較サイトの確認")
    st.write("記事を公開したら、以下のボタンから実際のサイトを確認してみましょう！")
    st.link_button("🌐 比較サイトを開く ↗", "https://amiyamura-cyber.github.io/air-log-site/", use_container_width=True)
