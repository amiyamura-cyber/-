import streamlit as st
import streamlit.components.v1 as components
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import random
import html

# ==========================================
# 1. ページ全体の設定（一番最初に書く必要があります）
# ==========================================
st.set_page_config(
    page_title="エアログ統合システム",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 各画面のHTMLコード定義（管理画面・比較サイト）
# ==========================================
HTML_MANAGEMENT = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>エアログ管理画面</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: #f0f2f5; color: #333; line-height: 1.6; }
  a { text-decoration: none; color: inherit; }
  img { max-width: 100%; display: block; }
  .l-header { background: #fff; padding: 16px 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
  .l-header__title { font-size: 1.25rem; font-weight: bold; color: #1a73e8; }
  .l-container { display: flex; max-width: 1400px; margin: 24px auto; padding: 0 24px; gap: 32px; align-items: flex-start; }
  .l-editor { flex: 0 0 500px; background: #fff; padding: 24px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); position: sticky; top: 88px; max-height: calc(100vh - 100px); overflow-y: auto; }
  .l-list { flex: 1; }
  .c-form-group { margin-bottom: 20px; }
  .c-label { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; font-weight: bold; margin-bottom: 8px; color: #555; }
  .c-input, .c-select, .c-textarea { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.95rem; font-family: inherit; transition: border-color 0.2s; }
  .c-input:focus, .c-select:focus, .c-textarea:focus { border-color: #1a73e8; outline: none; }
  .c-textarea { height: 120px; resize: vertical; line-height: 1.5; font-family: monospace; }
  .c-radio-group { display: flex; gap: 16px; }
  .c-radio-label { display: flex; align-items: center; gap: 6px; font-size: 0.9rem; cursor: pointer; }
  .c-date-group { display: flex; gap: 12px; align-items: center; }
  .c-date-group span { color: #888; }
  .c-toolbar { display: flex; gap: 8px; margin-bottom: 8px; background: #f8f9fa; padding: 8px; border-radius: 6px; border: 1px solid #ddd; }
  .c-toolbar-btn { background: #fff; border: 1px solid #ccc; padding: 4px 12px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; }
  .c-image-upload { border: 2px dashed #ddd; border-radius: 8px; padding: 20px; text-align: center; cursor: pointer; position: relative; overflow: hidden; background: #fafafa; }
  .c-image-upload input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
  .c-image-upload__preview { display: none; width: 100%; height: 180px; object-fit: cover; border-radius: 6px; margin-bottom: 12px; }
  .c-image-upload__text { font-size: 0.85rem; color: #888; }
  .c-btn-remove-img { display: none; background: #ef5350; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; margin: 0 auto; }
  .c-slider-group { display: none; margin-top: 12px; background: #f8f9fa; padding: 12px; border-radius: 6px; border: 1px solid #eee; }
  .c-slider-group label { font-size: 0.8rem; color: #555; display: block; margin-bottom: 8px; text-align: center; font-weight: bold; }
  .c-slider { width: 100%; cursor: pointer; }
  .c-btn { width: 100%; padding: 14px; border: none; border-radius: 6px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: background 0.2s; text-align: center; }
  .c-btn--primary { background: #1a73e8; color: #fff; }
  .c-btn--secondary { background: #e0e0e0; color: #333; margin-top: 12px; }
  .c-btn--small { padding: 4px 12px; font-size: 0.8rem; width: auto; margin: 0; }
  .c-btn-group { display: flex; gap: 12px; margin-top: 20px; }
  .c-btn-group .c-btn { margin-top: 0; }
  .l-list__header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 20px; }
  .l-list__title { font-size: 1.5rem; font-weight: bold; }
  .c-folder { margin-bottom: 24px; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow: hidden; }
  .c-folder summary { padding: 16px 24px; font-size: 1.1rem; font-weight: bold; background: #fff; cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid transparent; }
  .c-folder summary::after { content: "▼"; font-size: 0.8rem; color: #888; transition: transform 0.3s; }
  .c-folder[open] summary { border-bottom: 1px solid #eee; background: #f8f9fa; }
  .c-folder[open] summary::after { transform: rotate(180deg); }
  .c-folder__content { padding: 24px; background: #f0f2f5; }
  .p-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; }
  .p-card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform 0.2s; position: relative; display: flex; flex-direction: column; cursor: pointer; border: 1px solid transparent; }
  .p-card--private { opacity: 0.7; border-style: dashed; border-color: #999; }
  .p-card--private::after { content: '非公開'; position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: #fff; font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; z-index: 10; }
  .p-card__img { width: 100%; height: 180px; object-fit: cover; background: #eee; }
  .p-card__body { padding: 16px; flex: 1; display: flex; flex-direction: column; }
  .p-card__genre { align-self: flex-start; font-size: 0.7rem; color: #fff; background: #1a73e8; padding: 4px 10px; border-radius: 20px; margin-bottom: 12px; font-weight: bold; }
  .p-card__genre--採用支援 { background: #1a73e8; }
  .p-card__genre--集客支援 { background: #8e24aa; }
  .p-card__genre--お役立ち資料 { background: #43a047; }
  .p-card__genre--セミナー情報 { background: #f57c00; }
  .p-card__title { font-size: 1rem; font-weight: 700; line-height: 1.5; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .p-card__tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: auto; margin-bottom: 12px; }
  .p-card__tag { font-size: 0.7rem; color: #1a73e8; background: #e8f0fe; padding: 4px 8px; border-radius: 12px; font-weight: 500; }
  .p-card__footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 12px; }
  .p-card__date { font-size: 0.75rem; color: #888; }
  .p-card__actions { display: flex; gap: 6px; }
  .p-card__btn { padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; border: none; cursor: pointer; font-weight: bold; }
  .p-card__btn--copy { background: #e3f2fd; color: #1a73e8; }
  .p-card__btn--edit { background: #e0f2f1; color: #00897b; }
  .p-card__btn--delete { background: #ffebee; color: #e53935; }
  .c-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; display: none; align-items: center; justify-content: center; padding: 24px; opacity: 0; transition: opacity 0.3s; }
  .c-modal.is-open { display: flex; opacity: 1; }
  .c-modal__inner { background: #fff; width: 100%; max-width: 800px; max-height: 90vh; border-radius: 12px; overflow-y: auto; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
  .c-modal__close { position: absolute; top: 16px; right: 16px; background: #f0f0f0; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 10; }
  .p-article-preview__cover { width: 100%; height: 300px; object-fit: cover; }
  .p-article-preview__header { padding: 32px 32px 0; }
  .p-article-preview__meta { display: flex; gap: 12px; margin-bottom: 16px; align-items: center; }
  .p-article-preview__title { font-size: 1.8rem; font-weight: bold; margin-bottom: 16px; line-height: 1.4; }
  .p-article-preview__tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px; }
  .p-article-preview__content{padding:0 32px 32px;line-height:1.8;font-size:1.05rem;color:#333;}
  .p-article-preview__content p{margin-bottom:24px;}
  .p-article-preview__content a{color:#1a73e8;text-decoration:underline}
  .p-article-preview__content h2{margin: 40px 0 20px; font-size: 1.4rem; background-color: #f5f5f5; border-left: 6px solid #d44c7d; padding: 16px 20px; font-weight: 700;}
  .p-article-preview__content h3{margin: 32px 0 16px; font-size: 1.25rem; border-bottom: 2px solid #d44c7d; padding-bottom: 8px; font-weight: 700;}
  .c-empty-message { text-align: center; padding: 40px; background: #fff; border-radius: 12px; color: #888; font-size: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
</style>
</head>
<body>
<header class="l-header"><div class="l-header__title">エアログ 管理・編集画面</div></header>
<div class="l-container">
  <aside class="l-editor">
    <h2 style="font-size: 1.2rem; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px;">記事を編集</h2>
    <form id="postForm">
      <input type="hidden" id="postId">
      <div class="c-form-group">
        <label class="c-label"><span>ステータス</span></label>
        <div class="c-radio-group">
          <label class="c-radio-label"><input type="radio" name="status" value="public" checked> 公開</label>
          <label class="c-radio-label"><input type="radio" name="status" value="private"> 非公開 (下書き)</label>
        </div>
      </div>
      <div class="c-form-group">
        <label class="c-label"><span>カテゴリー</span></label>
        <select id="postGenre" class="c-select" required>
          <option value="" disabled selected>選択してください</option>
          <option value="採用支援">採用支援</option>
          <option value="集客支援">集客支援</option>
          <option value="お役立ち資料">お役立ち資料</option>
          <option value="セミナー情報">セミナー情報</option>
        </select>
      </div>
      <div class="c-form-group">
        <label class="c-label"><span>タイトル</span></label>
        <input type="text" id="postTitle" class="c-input" placeholder="記事のタイトルを入力" required>
      </div>
      <div class="c-form-group">
        <label class="c-label"><span>カバー画像</span></label>
        <div class="c-image-upload" id="imageUploadArea">
          <img id="imagePreview" class="c-image-upload__preview" src="" alt="Preview">
          <span class="c-image-upload__text" id="imageUploadText">クリックして画像をアップロード<br>(またはドラッグ＆ドロップ)</span>
          <input type="file" id="imageInput" accept="image/*">
        </div>
        <input type="hidden" id="coverImageData">
        <button type="button" id="btnRemoveImage" class="c-btn-remove-img" style="margin-top:8px;">画像を削除</button>
        <div class="c-slider-group" id="imageAdjustArea">
          <label>表示位置調整（左 ↔ 右）</label>
          <input type="range" id="imagePositionSliderX" class="c-slider" min="0" max="100" value="50">
          <label style="margin-top:12px;">表示位置調整（上 ↔ 下）</label>
          <input type="range" id="imagePositionSliderY" class="c-slider" min="0" max="100" value="50">
        </div>
      </div>
      <div class="c-form-group">
        <label class="c-label"><span>ハッシュタグ（カンマ区切り）</span></label>
        <input type="text" id="postTags" class="c-input" placeholder="例: 採用, 就活, 新卒, 中途">
      </div>
      <div class="c-form-group">
        <label class="c-label"><span>公開期間</span></label>
        <div class="c-date-group">
          <input type="date" id="startDate" class="c-input"><span>〜</span><input type="date" id="endDate" class="c-input">
        </div>
      </div>
      <div class="c-form-group">
        <label class="c-label">
          <span>本文 (HTMLソースコード)</span>
          <button type="button" id="btnExpandEditor" class="c-btn c-btn--primary c-btn--small">拡大して編集</button>
        </label>
        <div class="c-toolbar">
          <button type="button" class="c-toolbar-btn btn-link" data-target="postContent">リンク挿入/編集</button>
          <button type="button" class="c-toolbar-btn btn-bold" data-target="postContent">太字</button>
        </div>
        <textarea id="postContent" class="c-textarea" placeholder="<p>ここに記事のHTMLを記述します。</p>"></textarea>
      </div>
      <div class="c-btn-group">
        <button type="submit" class="c-btn c-btn--primary">保存する</button>
        <button type="button" id="btnPreviewInput" class="c-btn c-btn--secondary">プレビュー</button>
      </div>
      <button type="button" id="btnClear" class="c-btn c-btn--secondary">新規作成（クリア）</button>
    </form>
  </aside>
  <main class="l-list">
    <div class="l-list__header">
      <h2 class="l-list__title">記事一覧</h2>
      <span style="font-size: 0.9rem; color: #666;" id="articleCount">全 0 件</span>
    </div>
    <div id="articleGrid"></div>
  </main>
</div>
<!-- TEXT EDITOR MODAL -->
<div class="c-modal" id="textEditorModal">
  <div class="c-modal__inner" style="max-width: 900px; height: 85vh; display: flex; flex-direction: column; padding: 24px; overflow: hidden;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <h2 style="font-size: 1.3rem; color: #1a73e8;">本文の編集</h2>
      <button class="c-btn c-btn--primary" id="closeTextEditorModal" style="width: auto; padding: 10px 24px;">完了して閉じる</button>
    </div>
    <div class="c-toolbar" style="margin-bottom: 12px;">
      <button type="button" class="c-toolbar-btn btn-link" data-target="modalPostContent">リンク挿入/編集</button>
      <button type="button" class="c-toolbar-btn btn-bold" data-target="modalPostContent">太字</button>
    </div>
    <textarea id="modalPostContent" class="c-textarea" style="flex: 1; height: auto; resize: none; font-size: 1rem; padding: 16px; border-color: #ccc;"></textarea>
  </div>
</div>
<!-- PREVIEW MODAL -->
<div class="c-modal" id="previewModal">
  <div class="c-modal__inner">
    <button class="c-modal__close" id="closePreviewModal">&times;</button>
    <img id="previewCover" class="p-article-preview__cover" src="" alt="" style="display:none;">
    <div class="p-article-preview__header">
      <div class="p-article-preview__meta">
        <span id="previewGenre" class="p-card__genre" style="margin:0;"></span>
        <span id="previewDate" class="p-card__date" style="border:none; padding:0; margin:0;"></span>
      </div>
      <h1 id="previewTitle" class="p-article-preview__title"></h1>
      <div id="previewTags" class="p-article-preview__tags"></div>
    </div>
    <div id="previewContent" class="p-article-preview__content"></div>
  </div>
</div>
<script>
document.addEventListener('DOMContentLoaded', () => {
  const STORAGE_KEY = 'tralog_posts';
  const form = document.getElementById('postForm');
  const articleGrid = document.getElementById('articleGrid');
  const articleCount = document.getElementById('articleCount');
  
  const inputs = {
    id: document.getElementById('postId'), title: document.getElementById('postTitle'),
    genre: document.getElementById('postGenre'), tags: document.getElementById('postTags'),
    status: document.getElementsByName('status'), startDate: document.getElementById('startDate'),
    endDate: document.getElementById('endDate'), content: document.getElementById('postContent'),
    coverImageData: document.getElementById('coverImageData')
  };

  const imageInput = document.getElementById('imageInput');
  const imagePreview = document.getElementById('imagePreview');
  const imageUploadText = document.getElementById('imageUploadText');
  const btnRemoveImage = document.getElementById('btnRemoveImage');
  const imageAdjustArea = document.getElementById('imageAdjustArea');
  const imagePositionSliderX = document.getElementById('imagePositionSliderX');
  const imagePositionSliderY = document.getElementById('imagePositionSliderY');
  const previewModal = document.getElementById('previewModal');
  const closePreviewModal = document.getElementById('closePreviewModal');
  const textEditorModal = document.getElementById('textEditorModal');
  const btnExpandEditor = document.getElementById('btnExpandEditor');
  const closeTextEditorModal = document.getElementById('closeTextEditorModal');
  const modalPostContent = document.getElementById('modalPostContent');

  function loadData() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch(e) { return []; } }
  function saveData(data) { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch (e) { alert('【エラー】保存容量の限界に達しました。'); } }
  function generateId() { return 'post_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36); }
  function formatDate(dateObj) {
    const y = dateObj.getFullYear(), m = String(dateObj.getMonth() + 1).padStart(2, '0'), d = String(dateObj.getDate()).padStart(2, '0');
    return `${y}.${m}.${d}`;
  }

  imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
          const MAX_WIDTH = 800; let width = img.width, height = img.height;
          if (width > MAX_WIDTH) { height = Math.round((height * MAX_WIDTH) / width); width = MAX_WIDTH; }
          const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
          const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0, width, height);
          const compressedBase64 = canvas.toDataURL('image/jpeg', 0.7);
          inputs.coverImageData.value = compressedBase64; showImagePreview(compressedBase64);
        };
        img.src = event.target.result;
      };
      reader.readAsDataURL(file);
    }
  });

  function showImagePreview(src) {
    if (src) {
      imagePreview.src = src; imagePreview.style.display = 'block'; imageUploadText.style.display = 'none';
      btnRemoveImage.style.display = 'block'; imageAdjustArea.style.display = 'block';
      imagePreview.style.objectPosition = `${imagePositionSliderX.value}% ${imagePositionSliderY.value}%`;
    } else {
      imagePreview.src = ''; imagePreview.style.display = 'none'; imageUploadText.style.display = 'block';
      btnRemoveImage.style.display = 'none'; imageAdjustArea.style.display = 'none';
      inputs.coverImageData.value = ''; imageInput.value = '';
      imagePositionSliderX.value = 50; imagePositionSliderY.value = 50;
    }
  }

  function updatePreviewPosition() { imagePreview.style.objectPosition = `${imagePositionSliderX.value}% ${imagePositionSliderY.value}%`; }
  imagePositionSliderX.addEventListener('input', updatePreviewPosition);
  imagePositionSliderY.addEventListener('input', updatePreviewPosition);
  btnRemoveImage.addEventListener('click', () => showImagePreview(''));

  btnExpandEditor.addEventListener('click', () => { modalPostContent.value = inputs.content.value; textEditorModal.classList.add('is-open'); document.body.style.overflow = 'hidden'; });
  closeTextEditorModal.addEventListener('click', () => { inputs.content.value = modalPostContent.value; textEditorModal.classList.remove('is-open'); document.body.style.overflow = ''; });

  function renderGrid() {
    const posts = loadData();
    posts.sort((a, b) => new Date(b.date) - new Date(a.date));
    articleGrid.innerHTML = ''; articleCount.textContent = `全 ${posts.length} 件`;
    if (posts.length === 0) {
      articleGrid.innerHTML = '<div class="c-empty-message">記事がありません。<br>左のフォームから新規作成してください。</div>';
      return;
    }
    const groupedPosts = {};
    posts.forEach(post => {
      const [year, month] = post.displayDate.split('.'); const key = `${year}年${month}月`;
      if (!groupedPosts[key]) groupedPosts[key] = [];
      groupedPosts[key].push(post);
    });
    const keys = Object.keys(groupedPosts).sort((a, b) => a > b ? -1 : 1);
    keys.forEach((key, index) => {
      const group = groupedPosts[key];
      const details = document.createElement('details'); details.className = 'c-folder';
      if (index === 0) details.open = true;
      const summary = document.createElement('summary');
      summary.innerHTML = `<span>${key}</span> <span style="font-size: 0.9rem; font-weight: normal; color: #666;">${group.length} 件</span>`;
      details.appendChild(summary);
      const content = document.createElement('div'); content.className = 'c-folder__content';
      const grid = document.createElement('div'); grid.className = 'p-grid';
      group.forEach(post => {
        const card = document.createElement('div');
        card.className = `p-card ${post.status === 'private' ? 'p-card--private' : ''}`;
        const tagsHtml = post.tags && post.tags.length > 0 ? `<div class="p-card__tags">${post.tags.map(t => `<span class="p-card__tag">#${t}</span>`).join('')}</div>` : '';
        const defaultImg = `https://via.placeholder.com/400x200/e3f2fd/1a73e8?text=${encodeURIComponent(post.genre)}`;
        const imgSrc = post.coverImage || defaultImg;
        const posX = post.coverPositionX !== undefined ? post.coverPositionX : 50;
        const posY = post.coverPositionY !== undefined ? post.coverPositionY : 50;
        card.innerHTML = `
          <img class="p-card__img" src="${imgSrc}" alt="" style="object-position: ${posX}% ${posY}%;">
          <div class="p-card__body">
            <span class="p-card__genre p-card__genre--${post.genre}">${post.genre}</span>
            <h3 class="p-card__title">${post.title}</h3>
            ${tagsHtml}
            <div class="p-card__footer">
              <span class="p-card__date">更新: ${post.displayDate}</span>
              <div class="p-card__actions">
                <button type="button" class="p-card__btn p-card__btn--edit" data-id="${post.id}">編集</button>
                <button type="button" class="p-card__btn p-card__btn--delete" data-id="${post.id}">削除</button>
              </div>
            </div>
          </div>
        `;
        card.querySelector('.p-card__btn--edit').addEventListener('click', (e) => { e.stopPropagation(); editPost(post.id); });
        card.querySelector('.p-card__btn--delete').addEventListener('click', (e) => { e.stopPropagation(); deletePost(post.id); });
        card.addEventListener('click', () => openPreview(post));
        grid.appendChild(card);
      });
      content.appendChild(grid); details.appendChild(content); articleGrid.appendChild(details);
    });
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const posts = loadData(), isEdit = inputs.id.value !== '', now = new Date();
    let statusVal = 'public';
    for (const radio of inputs.status) if (radio.checked) statusVal = radio.value;
    const tagArray = inputs.tags.value.split(',').map(t => t.trim()).filter(t => t !== '');
    const postData = {
      id: isEdit ? inputs.id.value : generateId(), title: inputs.title.value, genre: inputs.genre.value,
      tags: tagArray, status: statusVal, startDate: inputs.startDate.value, endDate: inputs.endDate.value,
      content: inputs.content.value, coverImage: inputs.coverImageData.value,
      coverPositionX: imagePositionSliderX.value, coverPositionY: imagePositionSliderY.value,
      date: isEdit ? posts.find(p => p.id === inputs.id.value).date : now.toISOString(), displayDate: formatDate(now)
    };
    if (isEdit) { posts[posts.findIndex(p => p.id === postData.id)] = postData; } else { posts.push(postData); }
    saveData(posts); renderGrid(); clearForm(); alert('保存しました。');
  });

  function editPost(id) {
    const post = loadData().find(p => p.id === id); if (!post) return;
    inputs.id.value = post.id; inputs.title.value = post.title; inputs.genre.value = post.genre;
    inputs.tags.value = (post.tags || []).join(', '); inputs.startDate.value = post.startDate || '';
    inputs.endDate.value = post.endDate || ''; inputs.content.value = post.content || '';
    imagePositionSliderX.value = post.coverPositionX !== undefined ? post.coverPositionX : 50;
    imagePositionSliderY.value = post.coverPositionY !== undefined ? post.coverPositionY : 50;
    for (const radio of inputs.status) radio.checked = (radio.value === post.status);
    showImagePreview(post.coverImage || ''); window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function deletePost(id) { if (!confirm('本当に削除しますか？')) return; saveData(loadData().filter(p => p.id !== id)); renderGrid(); clearForm(); }
  function clearForm() { form.reset(); inputs.id.value = ''; inputs.coverImageData.value = ''; imagePositionSliderX.value = 50; imagePositionSliderY.value = 50; showImagePreview(''); inputs.status[0].checked = true; }
  document.getElementById('btnClear').addEventListener('click', clearForm);

  document.getElementById('btnPreviewInput').addEventListener('click', () => {
    const dummyPost = {
      title: inputs.title.value || '（タイトル未入力）', genre: inputs.genre.value || 'その他',
      tags: inputs.tags.value.split(',').map(t => t.trim()).filter(t => t !== ''),
      displayDate: formatDate(new Date()), coverImage: inputs.coverImageData.value,
      coverPositionX: imagePositionSliderX.value, coverPositionY: imagePositionSliderY.value, content: inputs.content.value
    };
    openPreview(dummyPost);
  });

  function openPreview(post) {
    document.getElementById('previewTitle').textContent = post.title; document.getElementById('previewGenre').textContent = post.genre;
    document.getElementById('previewGenre').className = `p-card__genre p-card__genre--${post.genre}`;
    document.getElementById('previewDate').textContent = post.displayDate;
    document.getElementById('previewTags').innerHTML = post.tags && post.tags.length > 0 ? post.tags.map(t => `<span class="p-card__tag">#${t}</span>`).join('') : '';
    const coverEl = document.getElementById('previewCover');
    if (post.coverImage) {
      coverEl.src = post.coverImage; coverEl.style.display = 'block';
      const posX = post.coverPositionX !== undefined ? post.coverPositionX : 50;
      const posY = post.coverPositionY !== undefined ? post.coverPositionY : 50;
      coverEl.style.objectPosition = `${posX}% ${posY}%`;
    } else { coverEl.style.display = 'none'; }
    document.getElementById('previewContent').innerHTML = post.content || '<p>本文がありません。</p>';
    previewModal.classList.add('is-open'); document.body.style.overflow = 'hidden';
  }

  closePreviewModal.addEventListener('click', () => { previewModal.classList.remove('is-open'); document.body.style.overflow = ''; });
  previewModal.addEventListener('click', (e) => { if (e.target === previewModal) { previewModal.classList.remove('is-open'); document.body.style.overflow = ''; } });
  renderGrid();
});
</script>
</body>
</html>
"""

HTML_COMPARISON = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>エアログ｜採用・集客を支援するメディア</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Hiragino Kaku Gothic ProN','Noto Sans JP',sans-serif;color:#333;line-height:1.7;background:#f9f9f9}
a{text-decoration:none;color:inherit;transition:opacity .2s}
a:hover{opacity:.7}
img{max-width:100%;height:auto;display:block}
ul,ol{list-style:none}
.l-header{background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.05);position:sticky;top:0;z-index:1000}
.l-header__inner{max-width:1200px;margin:0 auto;padding:16px 24px;display:flex;align-items:center;justify-content:space-between}
.l-header__logo{font-family: 'Hiragino Mincho ProN', 'ヒラギノ明朝 ProN W6', serif; font-size:1.8rem; font-weight:600; color:#d81b60; letter-spacing:-1px;}
.l-header__logo span{color:#333}
.l-header__nav{display:flex;gap:32px}
.l-header__nav a{font-size:.95rem;font-weight:600;color:#333}
.l-header__nav a:hover{color:#d81b60} 
.p-hero { width: 100%; margin: 24px 0 48px; position: relative; overflow: hidden; padding: 24px 0; }
.p-hero__track { display: flex; align-items: center; transition: transform 0.5s cubic-bezier(0.25, 1, 0.5, 1); }
.p-hero__slide { flex: 0 0 420px; padding: 0 12px; box-sizing: border-box; transition: all 0.5s ease; opacity: 0.4; transform: scale(0.85); cursor: pointer; }
.p-hero__slide.is-center { opacity: 1; transform: scale(1.05); z-index: 2; }
.p-hero__slide img { width: 100%; aspect-ratio: 16/9; object-fit: cover; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); border: 1px solid #eaeaea; background: #fff; }
.p-hero__btn { position: absolute; top: calc(50% - 14px); transform: translateY(-50%); background: rgba(50,50,50,0.8); color: #fff; border: none; width: 44px; height: 44px; border-radius: 50%; font-size: 1.2rem; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; }
.p-hero__btn--prev { left: 24px; } .p-hero__btn--next { right: 24px; }
.p-hero__dots { display: flex; justify-content: center; gap: 8px; margin-top: 24px; }
.p-hero__dot { width: 10px; height: 10px; border-radius: 50%; background: #ccc; cursor: pointer; }
.p-hero__dot.active { background: #d81b60; } 
.l-wrapper{max-width:1200px;margin:0 auto 40px;padding:0 24px;display:flex;gap:40px;align-items:flex-start}
.l-main{flex:1;min-width:0;}
.l-sidebar{width:320px;flex-shrink:0;position:sticky;top:100px}
.l-section{margin-bottom:60px}
.l-section__header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;border-bottom:2px solid #d81b60;padding-bottom:12px;} 
.l-section__title{font-size:1.4rem;font-weight:bold;color:#333}
.l-section__more{font-size:.85rem;color:#d81b60;font-weight:600} 
.p-card-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.p-card{background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.04);transition:transform .2s;display:flex;flex-direction:column;cursor:pointer;border:1px solid #eee}
.p-card:hover{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.08)}
.p-card__thumb{width:100%;height:150px;object-fit:cover;background:#f5f5f5;}
.p-card__body{padding:16px;display:flex;flex-direction:column;flex:1}
.p-card__meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.p-card__cat{font-size:.65rem;color:#fff;background:#1a73e8;padding:4px 10px;border-radius:4px;font-weight:bold;}
.p-card__cat--document{background:#43a047} .p-card__cat--seminar{background:#f57c00} .p-card__cat--customer{background:#8e24aa} .p-card__cat--contact{background:#607d8b}
.p-card__date{font-size:.7rem;color:#888;font-weight:500}
.p-card__title{font-size:.95rem;font-weight:700;line-height:1.5;margin-bottom:12px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.p-card__tags{display:flex;flex-wrap:wrap;gap:4px;margin-top:auto;}
.p-card__tag{font-size:.7rem;color:#666;background:#f0f0f0;padding:2px 8px;border-radius:4px;}
.c-sidebar-block { margin-bottom: 24px; }
.c-search-box { display: flex; align-items: center; border: 2px solid #333; border-radius: 30px; padding: 8px 16px; background: #fff; }
.c-search-box__input { border: none; outline: none; flex: 1; font-size: 0.95rem; padding: 6px 0; }
.c-line-banner { background: #ea7c1e; color: #fff; padding: 24px 20px; border-radius: 8px; text-align: center; }
.c-line-banner__btn { display: flex; align-items: center; justify-content: center; background: #fff; color: #111; font-weight: bold; padding: 12px; border-radius: 30px; border: 2px solid #111; }
.c-widget{background:#fff;border-radius:8px;padding:24px;margin-bottom:32px;box-shadow:0 2px 8px rgba(0,0,0,.04);border:1px solid #eee}
.c-widget__title{font-size:1.1rem;font-weight:bold;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #eee; display: flex; align-items: center;}
.c-widget__list li{margin-bottom:12px}
.c-widget__list a{display:flex;align-items:center;font-size:.9rem;color:#555;}
.p-article{background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.04);overflow:hidden;border:1px solid #eee;margin-bottom:60px;}
.p-article__cover{width:100%;height:400px;object-fit:cover;background:#f5f5f5;}
.p-article__inner{padding:48px 56px;}
.p-article__meta{display:flex;gap:16px;margin-bottom:20px;align-items:center}
.p-article__cat{font-size:.85rem;color:#fff;background:#1a73e8;padding:6px 16px;border-radius:4px;font-weight:bold;}
.p-article__title{font-size:2rem;font-weight:bold;margin-bottom:24px;line-height:1.4;}
.p-article__tags{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:40px;padding-bottom:24px;border-bottom:1px solid #eee;}
.p-article__tag{font-size:.85rem;color:#555;background:#f0f0f0;padding:6px 12px;border-radius:4px;}
.p-article__content{line-height:1.9;font-size:1.05rem;color:#333;}
.p-article__content p{margin-bottom:24px;}
.p-article__content a{color:#d81b60;text-decoration:underline}
.p-article__content h2{margin: 48px 0 24px; font-size: 1.45rem; background-color: #f5f5f5; border-left: 6px solid #d81b60; padding: 18px 24px; font-weight: 700;}
.p-article__content h3{margin: 40px 0 20px; font-size: 1.25rem; border-bottom: 2px solid #d81b60; padding-bottom: 10px; font-weight: 700;}
.p-cta-banner{background:linear-gradient(135deg,#f06292,#d81b60);border-radius:12px;padding:48px;text-align:center;color:#fff;margin-bottom:60px;}
.p-cta-banner h2{font-size:1.6rem;margin-bottom:16px;font-weight:bold}
.p-cta-banner__btn{display:inline-block;background:#fff;color:#d81b60;font-weight:bold;padding:16px 48px;border-radius:30px;font-size:1.05rem;}
.l-footer{background:#263238;color:#cfd8dc;padding:60px 24px 40px;margin-top:60px}
</style>
</head>
<body>
<header class="l-header">
  <div class="l-header__inner">
    <a href="index.html" class="l-header__logo">エア<span>ログ</span></a>
    <nav class="l-header__nav" id="globalNav">
      <a href="index.html#sec-new">新着記事</a>
      <a href="index.html#sec-recruit">採用支援</a>
      <a href="index.html#sec-customer">集客支援</a>
    </nav>
  </div>
</header>
<div id="topPageSliderWrapper" style="display: none;">
  <section class="p-hero" id="heroArea">
    <button class="p-hero__btn p-hero__btn--prev" id="heroPrev">&#10094;</button>
    <button class="p-hero__btn p-hero__btn--next" id="heroNext">&#10095;</button>
    <div class="p-hero__track" id="heroTrack"></div>
    <div class="p-hero__dots" id="heroDots"></div>
  </section>
</div>
<div class="l-wrapper">
  <main class="l-main">
    <div id="topPageContent" style="display: none;">
      <section class="l-section" id="sec-new"><div class="l-section__header"><h2 class="l-section__title">新着記事</h2></div><div class="p-card-grid"></div></section>
      <section class="l-section" id="sec-document"><div class="l-section__header"><h2 class="l-section__title">お役立ち資料</h2></div><div class="p-card-grid"></div></section>
      <section class="l-section" id="sec-recruit"><div class="l-section__header"><h2 class="l-section__title">採用支援</h2></div><div class="p-card-grid"></div></section>
    </div>
    <div id="articlePageContent" style="display: none;">
      <article class="p-article" id="articleContainer"></article>
    </div>
    <section class="p-cta-banner">
      <h2>採用のお悩み、まるっと解決！</h2>
      <a href="#" class="p-cta-banner__btn">無料相談はこちら</a>
    </section>
  </main>
  <aside class="l-sidebar">
    <div class="c-sidebar-block">
      <div class="c-search-box">
        <input type="text" id="searchInput" class="c-search-box__input" placeholder="気になるワードを検索">
      </div>
    </div>
    <div class="c-sidebar-block">
      <div class="c-line-banner">
        <h3 class="c-line-banner__title">エアログ公式LINEの<br>登録受付中！</h3>
        <a href="#" class="c-line-banner__btn">LINE登録はこちら</a>
      </div>
    </div>
  </aside>
</div>
<footer class="l-footer"><p style="text-align:center;">&copy; 2025 TRACOM Co.,Ltd.</p></footer>
<script>
const STORAGE_KEY = 'tralog_posts';
function loadPosts(){ try{ return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch(e) { return []; } }
function getGenreClass(genre) {
  if (genre === 'お役立ち資料') return 'document';
  if (genre === 'セミナー情報') return 'seminar';
  if (genre === '集客支援') return 'customer';
  if (genre === 'お問い合わせ') return 'contact';
  return '';
}
document.getElementById('searchInput').addEventListener('input', function(e) {
  const query = e.target.value.toLowerCase();
  const cards = document.querySelectorAll('.p-card');
  cards.forEach(card => {
    const title = card.querySelector('.p-card__title').textContent.toLowerCase();
    card.style.display = title.includes(query) ? 'flex' : 'none';
  });
});
const params = new URLSearchParams(window.location.search);
const articleId = params.get('id');

if (articleId) {
  document.getElementById('topPageSliderWrapper').style.display = 'none';
  document.getElementById('topPageContent').style.display = 'none';
  document.getElementById('articlePageContent').style.display = 'block';
  renderArticle(articleId);
} else {
  document.getElementById('topPageSliderWrapper').style.display = 'block';
  document.getElementById('topPageContent').style.display = 'block';
  document.getElementById('articlePageContent').style.display = 'none';
  renderHeroSlider(); 
  renderGridList();
}

function renderHeroSlider() {
  const allPosts = loadPosts();
  let publicPosts = allPosts.filter(p => p.status === 'public');
  const track = document.getElementById('heroTrack');
  track.innerHTML = '';
  let sliderPosts = [...publicPosts.sort(() => 0.5 - Math.random()).slice(0, 6)];
  while (sliderPosts.length < 6) { sliderPosts.push({ isDummy: true }); }
  sliderPosts.forEach(post => {
    if(post.isDummy) {
      track.innerHTML += `<div class="p-hero__slide"><img src="https://via.placeholder.com/800x450/eeeeee/bbbbbb?text=No+Article" alt=""></div>`;
    } else {
      const defaultImg = `https://via.placeholder.com/800x450/e3f2fd/1a73e8?text=${encodeURIComponent(post.genre || 'No Image')}`;
      const imgSrc = post.coverImage || defaultImg;
      const posX = post.coverPositionX !== undefined ? post.coverPositionX : 50;
      const posY = post.coverPositionY !== undefined ? post.coverPositionY : 50;
      track.innerHTML += `<div class="p-hero__slide" data-id="${post.id}"><img src="${imgSrc}" style="object-position: ${posX}% ${posY}%;"></div>`;
    }
  });
  initHeroSlider();
}

function initHeroSlider() {
  const track = document.getElementById('heroTrack');
  const slides = track.querySelectorAll('.p-hero__slide');
  if(slides.length === 0) return;
  let current = 0;
  function goTo(idx) {
    if(idx < 0) idx = slides.length - 1;
    if(idx >= slides.length) idx = 0;
    current = idx;
    const offset = -(current * slides[0].offsetWidth) + (document.getElementById('heroArea').offsetWidth / 2) - (slides[0].offsetWidth / 2);
    track.style.transform = `translateX(${offset}px)`;
    slides.forEach((slide, i) => { slide.classList.toggle('is-center', i === current); });
  }
  slides.forEach((slide, idx) => {
    slide.onclick = () => {
      if (idx === current && slide.dataset.id) window.location.href = `index.html?id=${slide.dataset.id}`;
      else goTo(idx);
    };
  });
  setTimeout(() => goTo(0), 50);
}

function renderGridList(){
  const allPosts = loadPosts();
  const publicPosts = allPosts.filter(p => p.status === 'public').sort((a,b) => new Date(b.date) - new Date(a.date));
  function createCard(post){
    const imgSrc = post.coverImage || `https://via.placeholder.com/600x400/e3f2fd/1a73e8?text=${encodeURIComponent(post.genre || 'No Image')}`;
    const catClass = getGenreClass(post.genre);
    const posX = post.coverPositionX !== undefined ? post.coverPositionX : 50;
    const posY = post.coverPositionY !== undefined ? post.coverPositionY : 50;
    return `
    <article class="p-card" data-id="${post.id}">
      <img class="p-card__thumb" src="${imgSrc}" style="object-position: ${posX}% ${posY}%;">
      <div class="p-card__body">
        <div class="p-card__meta"><span class="p-card__cat ${catClass ? 'p-card__cat--' + catClass : ''}">${post.genre || 'その他'}</span><time class="p-card__date">${post.displayDate || ''}</time></div>
        <h3 class="p-card__title">${post.title || '無題'}</h3>
      </div>
    </article>`;
  }
  const grids = { new: document.querySelector('#sec-new .p-card-grid'), recruit: document.querySelector('#sec-recruit .p-card-grid'), document: document.querySelector('#sec-document .p-card-grid') };
  if(grids.new) { grids.new.innerHTML = ''; publicPosts.slice(0, 6).forEach(p => grids.new.innerHTML += createCard(p)); }
  if(grids.recruit) { grids.recruit.innerHTML = ''; publicPosts.filter(p => p.genre === '採用支援').slice(0, 6).forEach(p => grids.recruit.innerHTML += createCard(p)); }
  if(grids.document) { grids.document.innerHTML = ''; publicPosts.filter(p => p.genre === 'お役立ち資料').slice(0, 6).forEach(p => grids.document.innerHTML += createCard(p)); }
}

function renderArticle(id) {
  const posts = loadPosts();
  const post = posts.find(p => p.id === id);
  const container = document.getElementById('articleContainer');
  if (!post || post.status !== 'public') {
    container.innerHTML = '<div style="padding:80px;text-align:center;">記事が存在しません。<br><a href="index.html">トップに戻る</a></div>'; return;
  }
  const catClass = getGenreClass(post.genre);
  const imgSrc = post.coverImage || `https://via.placeholder.com/1200x600/e3f2fd/1a73e8?text=${encodeURIComponent(post.genre)}`;
  const posX = post.coverPositionX !== undefined ? post.coverPositionX : 50;
  const posY = post.coverPositionY !== undefined ? post.coverPositionY : 50;
  container.innerHTML = `
    <img class="p-article__cover" src="${imgSrc}" style="object-position: ${posX}% ${posY}%;">
    <div class="p-article__inner">
      <div class="p-article__meta"><span class="p-article__cat ${catClass ? 'p-article__cat--' + catClass : ''}">${post.genre || 'その他'}</span><span class="p-article__date">更新日：${post.displayDate}</span></div>
      <h1 class="p-article__title">${post.title}</h1>
      <div class="p-article__content">${post.content || '<p>本文がありません。</p>'}</div>
    </div>
  `;
}
</script>
</body>
</html>
"""

# ==========================================
# 3. サイドバーでメニューを選択（ナビゲーション）
# ==========================================
st.sidebar.markdown("## ⚙️ エアログ統合メニュー")
page = st.sidebar.radio(
    "機能を選択してください",
    ["🔍 1. SEOキーワード抽出", "📝 2. 管理画面", "🤖 4. AI対話ボット", "🌐 3. 比較サイト"]
)
st.sidebar.markdown("---")

# ==========================================
# 4. 選んだメニューごとの画面表示処理
# ==========================================

# ------------------------------------------
# メニュー 1. SEOキーワード抽出（元々のアプリ）
# ------------------------------------------
if page == "🔍 1. SEOキーワード抽出":
    # 記憶エリアの初期化
    if "used_keywords" not in st.session_state: st.session_state.used_keywords = []
    if "search_clicked" not in st.session_state: st.session_state.search_clicked = False
    if "cur_grouped_keywords" not in st.session_state: st.session_state.cur_grouped_keywords = []
    if "cur_articles" not in st.session_state: st.session_state.cur_articles = []

    # カスタムCSS
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
            # （抽出処理は元コードと同じため短縮表示せず実行）
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
                            raw_pool.append({"title": t, "url": u, "summary": d[:100]})
                except Exception:
                    pass
            random.shuffle(raw_pool)
            clean_articles = raw_pool[:10]
            st.session_state.cur_articles = clean_articles

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


# ------------------------------------------
# メニュー 2. 管理画面
# ------------------------------------------
elif page == "📝 2. 管理画面":
    st.markdown("### 📝 記事管理・入稿画面")
    # Streamlitの中に直接HTMLを表示させます
    components.html(HTML_MANAGEMENT, height=1000, scrolling=True)


# ------------------------------------------
# メニュー 4. AI対話ボット（専用UI）
# ------------------------------------------
elif page == "🤖 4. AI対話ボット":
    st.markdown("### 🤖 記事作成 AIアシスタント")
    
    # 1. AIからの最初のメッセージをチャット風に表示
    with st.chat_message("assistant"):
        st.write("プロのSEOコンサルタント兼凄腕Webライターです！検索上位を狙えるSEO記事を作成します。まずは以下の**【3つの条件】**を教えてください。")

    # 2. ユーザーが条件を入力するエリア
    with st.form("prompt_form"):
        kw = st.text_input("1. 対策キーワード", placeholder="例：採用 企業向け")
        target = st.text_area("2. 記事の内容やターゲット", placeholder="例：採用に困っている中小企業の人事担当者向け。課題解決のノウハウを書きたい。")
        words = st.text_input("3. 文字数の目安", placeholder="例：10000文字程度")
        
        submitted = st.form_submit_button("✨ この条件でAIへの指示書（プロンプト）を生成する", type="primary")

    # 3. 入力完了後、完璧なプロンプトを自動生成
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
（必要な数だけliタグを繰り返す）
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

            st.success("✅ 指示書が完成しました！以下のテキストを右上のコピーボタンからコピーして、ChatGPTやGeminiに貼り付けてください。")
            st.code(prompt_text, language="text")
            
            # AIチャットへのジャンプボタン
            col1, col2 = st.columns(2)
            with col1:
                st.link_button("🤖 ChatGPT を開く ↗", "https://chatgpt.com/", use_container_width=True)
            with col2:
                st.link_button("🤖 Gemini を開く ↗", "https://gemini.google.com/app", use_container_width=True)


# ------------------------------------------
# メニュー 3. 比較サイト
# ------------------------------------------
elif page == "🌐 3. 比較サイト":
    st.markdown("### 🌐 比較サイト（フロントエンド）")
    components.html(HTML_COMPARISON, height=1000, scrolling=True)
