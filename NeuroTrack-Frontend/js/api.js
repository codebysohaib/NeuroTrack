/* Shared API layer — all fetch calls go through here */

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.12.1/firebase-auth.js";

const BASE = 'https://neurotrack-0q5m.onrender.com/api';

// ── Firebase Config ───────────────────────────────────────────────────────────
const firebaseConfig = {
  apiKey: "AIzaSyA5HUb6Mug3NJuhyrdhCKmxYXdx2O3Sris",
  authDomain: "neurotrack-cbs.firebaseapp.com",
  projectId: "neurotrack-cbs",
  storageBucket: "neurotrack-cbs.firebasestorage.app",
  messagingSenderId: "422832977385",
  appId: "1:422832977385:web:afbfb05adf0665f2e50778",
  measurementId: "G-ZYDVGCT5HF"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

// ── Helpers ──────────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw Object.assign(new Error(data.detail || data.error || 'Request failed'), { data, status: res.status });
  return data;
}

// ── Auth Actions ──────────────────────────────────────────────────────────────
export const signupEmail = (email, pass) => createUserWithEmailAndPassword(auth, email, pass);
export const loginEmail = (email, pass) => signInWithEmailAndPassword(auth, email, pass);
export const logout = () => {
  localStorage.removeItem('neurotrack_guest_id');
  return signOut(auth);
};

// ── User ID Logic (The "Smart" ID) ───────────────────────────────────────────
export function getUserId() {
  if (auth.currentUser) return auth.currentUser.uid;
  let guestId = localStorage.getItem('neurotrack_guest_id');
  if (!guestId) {
    guestId = 'guest_' + Math.random().toString(36).substring(2, 11);
    localStorage.setItem('neurotrack_guest_id', guestId);
  }
  return guestId;
}

// ── Health ────────────────────────────────────────────────────────────────────
export const ping        = ()      => apiFetch('/ping');
export const getHealth   = ()      => apiFetch('/health');
export const getVersion  = ()      => apiFetch('/version');

// ── Chat ──────────────────────────────────────────────────────────────────────
export const sendChat = (user_id, message, mood = '') =>
  apiFetch('/chat', { method: 'POST', body: JSON.stringify({ user_id, message, mood }) });

// ── Mood ──────────────────────────────────────────────────────────────────────
export const saveMood = (user_id, mood, note = '', intensity = null) =>
  apiFetch('/mood', { method: 'POST', body: JSON.stringify({ user_id, mood, note, intensity }) });

export const getMoodHistory = (user_id, limit = 30, mood_filter = '') =>
  apiFetch(`/mood/history?user_id=${encodeURIComponent(user_id)}&limit=${limit}${mood_filter ? '&mood=' + mood_filter : ''}`);

export const getMoodSummary = (user_id) =>
  apiFetch(`/mood/summary?user_id=${encodeURIComponent(user_id)}`);

// ── Suggestions ───────────────────────────────────────────────────────────────
export const getSuggestions  = (mood, count = 3) => apiFetch(`/suggestions?mood=${mood}&count=${count}`);
export const getAllSuggestions = ()              => apiFetch('/suggestions/all');
export const getSupportedMoods = ()             => apiFetch('/suggestions/moods');

// ── UI Helpers ────────────────────────────────────────────────────────────────
export function showToast(msg, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity .3s'; setTimeout(() => t.remove(), 300); }, duration);
}

export function setLoading(btn, loading, originalText) {
  if (loading) {
    btn.disabled = true;
    btn.dataset.orig = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span>`;
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.dataset.orig || originalText;
  }
}

export const MOOD_META = {
  happy:       { emoji: '😊', label: 'Happy' },
  sad:         { emoji: '😢', label: 'Sad' },
  anxious:     { emoji: '😰', label: 'Anxious' },
  angry:       { emoji: '😠', label: 'Angry' },
  stressed:    { emoji: '😤', label: 'Stressed' },
  tired:       { emoji: '😴', label: 'Tired' },
  lonely:      { emoji: '😔', label: 'Lonely' },
  overwhelmed: { emoji: '😵', label: 'Overwhelmed' },
  depressed:   { emoji: '😞', label: 'Depressed' },
  calm:        { emoji: '😌', label: 'Calm' },
  neutral:     { emoji: '😐', label: 'Neutral' },
};

export function moodEmoji(mood) {
  return MOOD_META[mood]?.emoji ?? '🙂';
}

export function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
