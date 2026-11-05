import re, json
src = open('/home/claude/hansang/index.html', encoding='utf-8').read()

def block(start_pat):
    i = src.index(start_pat)
    j = i
    if start_pat.startswith('function'):
        k = src.index('(', i); d = 0
        while True:
            if src[k] == '(': d += 1
            elif src[k] == ')':
                d -= 1
                if d == 0: break
            k += 1
        j = src.index('{', k)
    else:
        j = src.index('{', i)
    depth = 0
    k = j
    while True:
        c = src[k]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
        k += 1
    end = k + 1
    if end < len(src) and src[end] == ';': end += 1
    return src[i:end]

def line(start_pat):
    i = src.index(start_pat); j = src.index('\n', i); return src[i:j]

parts = []
for name in ['filt', 'gainN', 'lfo', 'repeat', 'burst', 'tone', 'bubble', 'softNoise', 'scatter', 'cheersClink', 'fwCrackle', 'sparklerLoop', 'crash', 'swash', 'pebbles', 'thunderFlash', 'catMeow', 'catPurr', 'gullCry', 'sfx', 'startLoop']:
    parts.append(block('function ' + name + '('))
parts.append(line('const noiseSrc = '))
parts.append(line('const chain = '))
parts.append(line('const WAVE_TYPES'))
parts.append(line('const RAIN_TYPES'))
parts.append(block('const MENUS = {'))
parts.append(block('const AMBIENCE = {'))
engine = '\n'.join(parts)

html = r'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>한 상 — 소리 실험실</title>
<style>
  :root { --bg:#f6f1e8; --card:#fffdf8; --ink:#2a2420; --muted:#8a7f72; --accent:#d8562e; --line:#e6dccd; --good:#3a8a5a; --fix:#c8402a; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; background: var(--bg); color: var(--ink); }
  header { position: sticky; top: 0; z-index: 5; background: rgba(246,241,232,0.94); backdrop-filter: blur(8px); border-bottom: 1px solid var(--line); padding: 14px 20px; display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
  header h1 { font-size: 20px; margin: 0 8px 0 0; }
  header .sub { color: var(--muted); font-size: 13px; flex: 1 1 260px; }
  header label { font-size: 13px; color: var(--muted); display: flex; gap: 6px; align-items: center; }
  button { font: inherit; cursor: pointer; }
  .btn { border: 1px solid var(--line); background: #fff; border-radius: 999px; padding: 7px 14px; font-size: 14px; }
  .btn.primary { background: var(--accent); color: #fff; border-color: var(--accent); }
  .btn.stop { background: var(--ink); color: #fff; border-color: var(--ink); }
  canvas#meter { width: 140px; height: 28px; background: #fff; border-radius: 8px; border: 1px solid var(--line); }
  main { max-width: 1100px; margin: 0 auto; padding: 18px 20px 120px; }
  section { margin-bottom: 26px; }
  section h2 { font-size: 17px; margin: 0 0 4px; }
  section p.d { margin: 0 0 12px; color: var(--muted); font-size: 13px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; }
  .card { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 14px; display: flex; flex-direction: column; gap: 9px; }
  .card.playing { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(216,86,46,0.15); }
  .card.good { border-left: 5px solid var(--good); }
  .card.fix { border-left: 5px solid var(--fix); }
  .top { display: flex; align-items: center; gap: 10px; }
  .play { width: 44px; height: 44px; border-radius: 50%; border: none; background: var(--accent); color: #fff; font-size: 18px; flex: none; }
  .card.playing .play { background: var(--ink); }
  .name { font-weight: 600; font-size: 15px; }
  .where { font-size: 12px; color: var(--muted); }
  .tag { font-size: 11px; padding: 2px 7px; border-radius: 999px; background: #efe7da; color: #7a6a58; margin-left: 4px; }
  .row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--muted); }
  .row input[type=range] { flex: 1; accent-color: var(--accent); }
  .row span.v { width: 34px; text-align: right; }
  .verdict { display: flex; gap: 6px; }
  .verdict button { flex: 1; border: 1px solid var(--line); background: #fff; border-radius: 10px; padding: 6px; font-size: 13px; }
  .verdict button.on.good { background: var(--good); color: #fff; border-color: var(--good); }
  .verdict button.on.fix { background: var(--fix); color: #fff; border-color: var(--fix); }
  textarea { width: 100%; min-height: 44px; border: 1px solid var(--line); border-radius: 10px; padding: 8px; font: inherit; font-size: 13px; resize: vertical; background: #fff; }
  .chips { display: flex; flex-wrap: wrap; gap: 5px; }
  .chips button { border: 1px dashed var(--line); background: transparent; border-radius: 999px; padding: 3px 9px; font-size: 12px; color: #6a5e50; }
  #out { position: fixed; left: 50%; bottom: 16px; transform: translateX(-50%); background: var(--ink); color: #fff; border-radius: 18px; padding: 10px 14px; display: flex; gap: 10px; align-items: center; box-shadow: 0 8px 30px rgba(0,0,0,0.25); z-index: 6; font-size: 14px; }
  #out .btn { background: #fff; color: var(--ink); border: none; }
  #sheet { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: none; align-items: center; justify-content: center; z-index: 9; }
  #sheet .box { background: #fff; border-radius: 18px; padding: 18px; width: min(640px, 92vw); }
  #sheet textarea { min-height: 260px; }
  #flash { position: fixed; inset: 0; background: #eef4ff; opacity: 0; pointer-events: none; z-index: 8; }
</style></head><body>
<div id="flash"></div>
<header>
  <h1>🎧 소리 실험실</h1>
  <div class="sub">「한 상」에 들어 있는 모든 소리예요. ▶를 눌러 하나씩 들어 보고, 👍 좋아요 / 🔧 고쳐줘를 고른 뒤 느낌을 적어 주세요. 다 듣고 아래 <b>‘메모 모아 보기’</b>를 눌러 복사해서 채팅에 붙여 주시면 그대로 반영할게요.</div>
  <label>전체 볼륨 <input id="mvol" type="range" min="0" max="150" value="80"></label>
  <canvas id="meter" width="280" height="56"></canvas>
  <button class="btn stop" id="stopAll">■ 모두 멈추기</button>
</header>
<main id="main"></main>
<div id="out"><span id="count">메모 0개</span><button class="btn" id="collect">📋 메모 모아 보기</button></div>
<div id="sheet"><div class="box"><h3 style="margin:0 0 8px">아래 내용을 복사해서 채팅에 붙여 주세요</h3><textarea id="sheetText"></textarea>
<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:10px"><button class="btn" id="copyBtn">복사하기</button><button class="btn primary" id="closeSheet">닫기</button></div></div></div>
<script>
// ---------- 실험실용 기본 장치 (실제 앱과 같은 소리 함수를 그대로 쓴다) ----------
const THREE = { Vector3: class { constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; } clone() { return new THREE.Vector3(this.x, this.y, this.z); } distanceTo() { return 0; } } };
const $ = (s) => document.querySelector(s);
const state = { waveType: 'beach', rainType: 'shower' }, SC = { wind: 0.6 }, W = { gust: 0 }, pivot = new THREE.Vector3();
const Sound = { ctx: null, master: null, bus: {}, noise: null };
function initAudio() {
  if (Sound.ctx) return; const ctx = new (window.AudioContext || window.webkitAudioContext)(); Sound.ctx = ctx;
  Sound.master = ctx.createGain(); Sound.master.gain.value = 0.8 * 1.2;
  Sound.analyser = ctx.createAnalyser(); Sound.analyser.fftSize = 512; Sound.master.connect(Sound.analyser); Sound.analyser.connect(ctx.destination);
  const len = ctx.sampleRate * 3, buf = ctx.createBuffer(1, len, ctx.sampleRate), d = buf.getChannelData(0); for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1; Sound.noise = buf;
  drawMeter();
}
// 실험실에서는 위치감 없이 바로 들리게 (앱에서는 소리가 나는 자리에서 들린다)
function makePanner(x, y, z, ref, dest) { const g = Sound.ctx.createGain(); g.gain.value = 0.8; g.connect(dest); return g; }
''' + engine + r'''

// ---------- 소리 목록 ----------
const fakeP = { isMe: true, head: null };
const at = () => new THREE.Vector3();
const S = [
  { cat: 'food', id: 'boil', name: '보글보글 끓는 소리', where: '라면·국밥·마라탕이 나온 처음 몇 초 (천천히)', loop: () => { const p = { isMe: true, menu: 'ramen', dish: { position: at() } }; startLoop(p); return p.stopLoop; } },
  { cat: 'food', id: 'sizzle', name: '치이익 굽는 소리', where: '삼겹살 앞에서 가끔', loop: () => { const p = { isMe: true, menu: 'samgyeop', dish: { position: at() } }; startLoop(p); return p.stopLoop; } },
  { cat: 'food', id: 'slurp', name: '호호 불고 호로록 (면 먹기)', where: '라면 한 입', play: () => sfx(fakeP, 'slurp', at()) },
  { cat: 'food', id: 'nom', name: '찹찹', where: '도시락·쌈 한 입', play: () => sfx(fakeP, 'nom', at()) },
  { cat: 'food', id: 'bite', name: '치킨 바사삭', where: '치킨 한 입', play: () => sfx(fakeP, 'bite', at()) },
  { cat: 'food', id: 'gulp', name: '꿀꺽 (물 마시기)', where: '물 마시기', play: () => sfx(fakeP, 'gulp', at()) },
  { cat: 'food', id: 'cheers', name: '다 같이 짠!', where: '🍻 짠 버튼 (여럿이 부딪힘)', play: () => { const c = makePanner(0, 0, 0, 1, Sound.bus.food); cheersClink(c); } },
  { cat: 'food', id: 'pour', name: '물 따르기 꼴꼴꼴', where: '리필 → 물', play: () => sfx(fakeP, 'pour', at()) },

  ...WAVE_TYPES.map(([v, label]) => ({ cat: 'waves', id: 'wave-' + v, name: label, where: '파도 소리 종류: ' + label, tag: '계속', loop: () => { state.waveType = v; return AMBIENCE.waves(); } })),
  { cat: 'waves', id: 'splash', name: '발이 물에 닿는 찰랑', where: '물가를 걸을 때', play: () => sfx(fakeP, 'splash', at()) },

  ...RAIN_TYPES.map(([v, label]) => ({ cat: 'rain', id: 'rain-' + v, name: label, where: '빗소리 종류: ' + label, tag: '계속', loop: () => { state.rainType = v; return AMBIENCE.rain(); } })),

  { cat: 'wind', id: 'wind', name: '바닷바람', where: '항상 (바람 세기에 따라)', tag: '계속', loop: () => AMBIENCE.wind() },

  { cat: 'animals', id: 'gull', name: '갈매기 끼룩끼룩', where: '해변 하늘, 새우깡 줄 때', play: () => gullCry(at(), 3) },
  { cat: 'animals', id: 'purr', name: '골골송 (골골골)', where: '고양이 쓰다듬기', play: () => catPurr({ g: { position: at() } }) },
  { cat: 'animals', id: 'cicadas', name: '매미', where: '여름 낮', tag: '계속', loop: () => AMBIENCE.cicadas() },
  { cat: 'animals', id: 'crickets', name: '귀뚜라미', where: '여름·가을 밤', tag: '계속', loop: () => AMBIENCE.crickets() },
  { cat: 'animals', id: 'birds', name: '참새 짹짹', where: '봄 아침·낮', tag: '계속', loop: () => AMBIENCE.birds() },

  { cat: 'etc', id: 'stepSand', name: '모래 위 저벅저벅', where: '해변을 걸을 때 한 걸음', play: () => { for (let i = 0; i < 4; i++) setTimeout(() => sfx(fakeP, 'stepSand', at()), i * 380); } },
  { cat: 'etc', id: 'stepWood', name: '나무 데크 발소리', where: '데크 위 한 걸음', play: () => { for (let i = 0; i < 4; i++) setTimeout(() => sfx(fakeP, 'stepWood', at()), i * 380); } },
  { cat: 'etc', id: 'whistle', name: '폭죽 퐁 (쏘아 올릴 때)', where: '폭죽이 올라갈 때', play: () => sfx(fakeP, 'whistle', at()) },
  { cat: 'etc', id: 'boom', name: '폭죽 둥- (멀리서)', where: '폭죽이 터질 때', play: () => sfx(fakeP, 'boom', at()) },
  { cat: 'etc', id: 'crackle', name: '폭죽 타닥타닥', where: '반짝이 폭죽 끝', play: () => { const far = makePanner(0, 0, 0, 25, Sound.bus.etc); fwCrackle(far); } },
  { cat: 'etc', id: 'sparkler', name: '손 폭죽 불티 틱틱', where: '손 폭죽 들고 있는 동안', tag: '계속', loop: () => sparklerLoop(makePanner(0, 0, 0, 0.8, Sound.bus.etc)) },
];
const CATS = [['food', '😋 음식', '내 식탁에서만 들려요'], ['waves', '🌊 파도', '파도 소리 종류는 소리 조절 창에서 고를 수 있어요'], ['rain', '☔ 비', '비 오는 날에만 들려요'], ['wind', '🍃 바람', ''], ['animals', '🪽 동물', ''], ['etc', '✨ 그 밖의 소리', '발소리, 문, 폭죽 등 (전체 볼륨만 따라가요)']];
const CHIPS = ['너무 커요', '너무 작아요', '둔탁해요', '날카로워요', '소음 같아요', '진짜 같지 않아요', '너무 자주 나요', '좋아요 그대로'];

// ---------- 화면 ----------
let notes = {}; try { notes = JSON.parse(localStorage.getItem('hansang.soundlab') || '{}'); } catch (e) {}
const save = () => { try { localStorage.setItem('hansang.soundlab', JSON.stringify(notes)); } catch (e) {} updateCount(); };
const running = {};
function stopOne(id) { if (running[id]) { try { running[id](); } catch (e) {} delete running[id]; } const c = document.getElementById('c-' + id); if (c) { c.classList.remove('playing'); c.querySelector('.play').textContent = '▶'; } }
function stopAll() { Object.keys(running).forEach(stopOne); }
function busFor(s) { const g = Sound.ctx.createGain(); g.gain.value = (s.vol ?? 100) / 100 * 1.0; g.connect(Sound.master); return g; }
function playSound(s) {
  initAudio(); if (Sound.ctx.state === 'suspended') Sound.ctx.resume();
  const c = document.getElementById('c-' + s.id);
  if (s.loop && running[s.id]) { stopOne(s.id); return; }
  const g = busFor(s); s.node = g; ['food', 'waves', 'wind', 'rain', 'animals', 'etc'].forEach((b) => (Sound.bus[b] = g));
  if (s.loop) { if (s.cat === 'waves') Object.keys(running).filter((k) => k.startsWith('wave-')).forEach(stopOne); if (s.cat === 'rain') Object.keys(running).filter((k) => k.startsWith('rain-')).forEach(stopOne);
    running[s.id] = s.loop(); c.classList.add('playing'); c.querySelector('.play').textContent = '■'; }
  else { s.play(); c.classList.add('playing'); setTimeout(() => c.classList.remove('playing'), 900); }
}
function render() {
  const main = $('#main');
  CATS.forEach(([cat, title, desc]) => {
    const sec = document.createElement('section'); sec.innerHTML = `<h2>${title}</h2>${desc ? `<p class="d">${desc}</p>` : '<p class="d"></p>'}<div class="grid"></div>`; main.appendChild(sec);
    S.filter((s) => s.cat === cat).forEach((s) => {
      const n = notes[s.id] || {}; s.vol = 100;
      const c = document.createElement('div'); c.className = 'card' + (n.v ? ' ' + n.v : ''); c.id = 'c-' + s.id;
      c.innerHTML = `<div class="top"><button class="play" aria-label="${s.name} 재생">▶</button><div><div class="name">${s.name}${s.loop ? '<span class="tag">계속 · 다시 누르면 멈춤</span>' : ''}</div><div class="where">${s.where}</div></div></div>
        <div class="row">이 소리 크기 <input type="range" min="0" max="200" value="100"><span class="v">100%</span></div>
        <div class="verdict"><button class="good${n.v === 'good' ? ' on' : ''}">👍 좋아요</button><button class="fix${n.v === 'fix' ? ' on' : ''}">🔧 고쳐줘</button></div>
        <div class="chips">${CHIPS.map((t) => `<button>${t}</button>`).join('')}</div>
        <textarea placeholder="어떻게 바뀌면 좋을지 자유롭게 적어 주세요 (예: 더 촉촉하게, 반으로 작게)">${n.t || ''}</textarea>`;
      c.querySelector('.play').onclick = () => playSound(s);
      const r = c.querySelector('input[type=range]'), rv = c.querySelector('.v');
      r.oninput = () => { s.vol = +r.value; rv.textContent = r.value + '%'; if (s.node && Sound.ctx) s.node.gain.setTargetAtTime(s.vol / 100, Sound.ctx.currentTime, 0.05); notes[s.id] = Object.assign(notes[s.id] || {}, { vol: s.vol }); save(); };
      if (n.vol) { r.value = n.vol; s.vol = n.vol; rv.textContent = n.vol + '%'; }
      c.querySelectorAll('.verdict button').forEach((b) => (b.onclick = () => { const v = b.classList.contains('good') ? 'good' : 'fix'; const cur = (notes[s.id] || {}).v === v ? null : v; notes[s.id] = Object.assign(notes[s.id] || {}, { v: cur }); c.classList.remove('good', 'fix'); if (cur) c.classList.add(cur); c.querySelectorAll('.verdict button').forEach((x) => x.classList.toggle('on', x.classList.contains(cur || '_'))); save(); }));
      const ta = c.querySelector('textarea'); ta.oninput = () => { notes[s.id] = Object.assign(notes[s.id] || {}, { t: ta.value }); save(); };
      c.querySelectorAll('.chips button').forEach((b) => (b.onclick = () => { ta.value = (ta.value ? ta.value.trim() + ', ' : '') + b.textContent; ta.oninput(); if (b.textContent === '좋아요 그대로') c.querySelector('.verdict .good').classList.contains('on') || c.querySelector('.verdict .good').click(); else if (!c.querySelector('.verdict .fix').classList.contains('on')) c.querySelector('.verdict .fix').click(); }));
      sec.querySelector('.grid').appendChild(c);
    });
  });
}
function updateCount() { const k = Object.values(notes).filter((n) => n.v || (n.t && n.t.trim()) || (n.vol && n.vol !== 100)).length; $('#count').textContent = `메모 ${k}개`; }
function collect() {
  const lines = ['[한 상 소리 실험실 메모]'];
  CATS.forEach(([cat, title]) => { const items = S.filter((s) => s.cat === cat).map((s) => { const n = notes[s.id] || {}; if (!n.v && !(n.t && n.t.trim()) && !(n.vol && n.vol !== 100)) return null; return `- ${s.name}: ${n.v === 'good' ? '👍 좋아요' : n.v === 'fix' ? '🔧 고쳐줘' : ''}${n.vol && n.vol !== 100 ? ` (크기 ${n.vol}%로)` : ''}${n.t && n.t.trim() ? ' — ' + n.t.trim() : ''}`; }).filter(Boolean); if (items.length) lines.push('', title, ...items); });
  if (lines.length === 1) lines.push('', '(아직 메모가 없어요)');
  $('#sheetText').value = lines.join('\n'); $('#sheet').style.display = 'flex';
}
function drawMeter() {
  const cv = $('#meter'), g = cv.getContext('2d'), a = Sound.analyser, buf = new Uint8Array(a.fftSize);
  const loop = () => { a.getByteTimeDomainData(buf); g.clearRect(0, 0, cv.width, cv.height); g.strokeStyle = '#d8562e'; g.lineWidth = 2; g.beginPath(); for (let i = 0; i < buf.length; i++) { const x = (i / buf.length) * cv.width, y = (buf[i] / 255) * cv.height; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); requestAnimationFrame(loop); };
  loop();
}
render(); updateCount();
$('#stopAll').onclick = stopAll;
$('#mvol').oninput = (e) => { initAudio(); Sound.master.gain.setTargetAtTime((+e.target.value / 100) * 1.2, Sound.ctx.currentTime, 0.05); };
$('#collect').onclick = collect; $('#closeSheet').onclick = () => ($('#sheet').style.display = 'none');
$('#copyBtn').onclick = async () => { const t = $('#sheetText'); t.select(); try { await navigator.clipboard.writeText(t.value); $('#copyBtn').textContent = '복사했어요 ✓'; } catch (e) { document.execCommand('copy'); $('#copyBtn').textContent = '복사했어요 ✓'; } setTimeout(() => ($('#copyBtn').textContent = '복사하기'), 1500); };
</script></body></html>
'''
open('/home/claude/hansang/soundlab.html', 'w', encoding='utf-8').write(html)
print('ok', len(html))
