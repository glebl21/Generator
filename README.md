<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TG Media Bot — Документация</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Unbounded:wght@400;700;900&family=Manrope:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #111118;
    --border: #1e1e2e;
    --accent: #5b6cff;
    --accent2: #ff6b9d;
    --accent3: #00d4aa;
    --text: #e8e8f0;
    --muted: #666680;
    --code-bg: #0d0d16;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Manrope', sans-serif;
    font-size: 15px;
    line-height: 1.7;
    overflow-x: hidden;
  }

  /* ── NOISE OVERLAY ── */
  body::before {
    content: '';
    position: fixed; inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none; z-index: 0; opacity: .4;
  }

  /* ── HERO ── */
  .hero {
    position: relative;
    min-height: 100vh;
    display: flex; flex-direction: column; justify-content: center;
    padding: 80px 60px;
    overflow: hidden;
  }

  .hero-grid {
    position: absolute; inset: 0;
    background-image:
      linear-gradient(rgba(91,108,255,.06) 1px, transparent 1px),
      linear-gradient(90deg, rgba(91,108,255,.06) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black, transparent);
  }

  .hero-glow {
    position: absolute;
    width: 700px; height: 700px;
    background: radial-gradient(circle, rgba(91,108,255,.15) 0%, transparent 70%);
    top: -200px; right: -200px;
    pointer-events: none;
  }
  .hero-glow2 {
    position: absolute;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(0,212,170,.10) 0%, transparent 70%);
    bottom: -150px; left: -100px;
    pointer-events: none;
  }

  .badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(91,108,255,.12);
    border: 1px solid rgba(91,108,255,.3);
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    padding: 6px 14px;
    border-radius: 100px;
    margin-bottom: 28px;
    width: fit-content;
    animation: fadeUp .6s ease both;
  }
  .badge-dot { width: 7px; height: 7px; background: var(--accent3); border-radius: 50%; animation: pulse 2s infinite; }

  @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.4)} }

  h1 {
    font-family: 'Unbounded', sans-serif;
    font-size: clamp(42px, 7vw, 84px);
    font-weight: 900;
    line-height: .95;
    letter-spacing: -2px;
    animation: fadeUp .6s .1s ease both;
  }

  h1 .line1 { display: block; }
  h1 .line2 {
    display: block;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }

  .hero-sub {
    margin-top: 24px;
    font-size: 17px;
    color: var(--muted);
    max-width: 500px;
    animation: fadeUp .6s .2s ease both;
  }

  .hero-meta {
    display: flex; gap: 32px; margin-top: 40px;
    animation: fadeUp .6s .3s ease both;
  }
  .meta-item { display: flex; flex-direction: column; gap: 4px; }
  .meta-val { font-family: 'Unbounded', sans-serif; font-size: 22px; font-weight: 700; color: var(--text); }
  .meta-label { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* ── LAYOUT ── */
  .container { max-width: 960px; margin: 0 auto; padding: 0 40px 120px; }

  /* ── SECTION ── */
  .section { margin-bottom: 80px; }
  .section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 12px;
  }
  h2 {
    font-family: 'Unbounded', sans-serif;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 32px;
    letter-spacing: -1px;
  }
  h3 {
    font-family: 'Unbounded', sans-serif;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 16px;
    color: var(--text);
  }

  /* ── SERVICES GRID ── */
  .services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
  }

  .service-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    transition: border-color .3s, transform .3s;
  }
  .service-card:hover { border-color: rgba(91,108,255,.4); transform: translateY(-3px); }
  .service-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--card-accent, var(--accent)), transparent);
  }
  .service-card.img { --card-accent: #5b6cff; }
  .service-card.vid { --card-accent: #ff6b9d; }
  .service-card.free { --card-accent: #00d4aa; }

  .service-icon { font-size: 28px; margin-bottom: 12px; }
  .service-name { font-family: 'Unbounded', sans-serif; font-size: 14px; font-weight: 700; margin-bottom: 6px; }
  .service-desc { font-size: 13px; color: var(--muted); margin-bottom: 14px; line-height: 1.5; }
  .service-tag {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 100px;
    border: 1px solid;
  }
  .tag-blue { color: var(--accent); border-color: rgba(91,108,255,.3); background: rgba(91,108,255,.08); }
  .tag-green { color: var(--accent3); border-color: rgba(0,212,170,.3); background: rgba(0,212,170,.08); }
  .tag-pink { color: var(--accent2); border-color: rgba(255,107,157,.3); background: rgba(255,107,157,.08); }

  /* ── STEPS ── */
  .steps { display: flex; flex-direction: column; gap: 0; }
  .step {
    display: flex; gap: 24px;
    padding: 28px 0;
    border-bottom: 1px solid var(--border);
  }
  .step:last-child { border-bottom: none; }
  .step-num {
    flex-shrink: 0;
    width: 40px; height: 40px;
    background: rgba(91,108,255,.12);
    border: 1px solid rgba(91,108,255,.3);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Unbounded', sans-serif;
    font-size: 14px; font-weight: 700;
    color: var(--accent);
  }
  .step-content { flex: 1; }
  .step-title { font-weight: 600; font-size: 15px; margin-bottom: 6px; }
  .step-desc { color: var(--muted); font-size: 14px; }
  .step-link {
    color: var(--accent);
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    display: inline-flex; align-items: center; gap: 5px;
    margin-top: 8px;
    transition: opacity .2s;
  }
  .step-link:hover { opacity: .7; }

  /* ── CODE BLOCK ── */
  .code-block {
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    margin: 20px 0;
  }
  .code-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 20px;
    border-bottom: 1px solid var(--border);
  }
  .code-dots { display: flex; gap: 6px; }
  .code-dots span { width: 10px; height: 10px; border-radius: 50%; }
  .dot-r { background: #ff5f57; }
  .dot-y { background: #febc2e; }
  .dot-g { background: #28c840; }
  .code-lang {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
  }
  pre {
    padding: 20px;
    overflow-x: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    line-height: 1.7;
    color: #c9d1e0;
  }
  .kw { color: #7c6af7; }
  .str { color: #7ec8a0; }
  .cmt { color: #4a5568; font-style: italic; }
  .var { color: #e06c75; }
  .fn { color: #61afef; }

  /* ── DEPLOY CARDS ── */
  .deploy-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
  }
  .deploy-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    transition: all .3s;
  }
  .deploy-card:hover { border-color: rgba(91,108,255,.3); }
  .deploy-card.recommended {
    border-color: rgba(91,108,255,.4);
    background: linear-gradient(135deg, rgba(91,108,255,.05), var(--surface));
  }
  .rec-badge {
    display: inline-block;
    background: var(--accent);
    color: white;
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
    padding: 3px 10px; border-radius: 100px;
    margin-bottom: 14px;
  }
  .deploy-title { font-family: 'Unbounded', sans-serif; font-size: 16px; font-weight: 700; margin-bottom: 8px; }
  .deploy-sub { font-size: 13px; color: var(--muted); margin-bottom: 16px; }
  .deploy-steps { list-style: none; display: flex; flex-direction: column; gap: 8px; }
  .deploy-steps li {
    font-size: 13px;
    display: flex; gap: 10px; align-items: flex-start;
  }
  .deploy-steps li::before {
    content: '→';
    color: var(--accent);
    flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace;
  }

  /* ── COMMANDS TABLE ── */
  .cmd-table { width: 100%; border-collapse: collapse; }
  .cmd-table th {
    text-align: left;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--muted);
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
  }
  .cmd-table td {
    padding: 14px 16px;
    border-bottom: 1px solid rgba(30,30,46,.5);
    font-size: 14px;
  }
  .cmd-table tr:last-child td { border-bottom: none; }
  .cmd-table tr:hover td { background: rgba(255,255,255,.02); }
  code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--accent);
    background: rgba(91,108,255,.1);
    padding: 2px 8px;
    border-radius: 5px;
  }

  /* ── TIPS ── */
  .tips-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }
  .tip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    font-size: 13px;
    color: var(--muted);
    line-height: 1.6;
  }
  .tip strong { color: var(--text); display: block; margin-bottom: 6px; font-size: 14px; }

  /* ── DIVIDER ── */
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 0 0 80px;
  }

  /* ── FOOTER ── */
  footer {
    border-top: 1px solid var(--border);
    padding: 40px;
    text-align: center;
    color: var(--muted);
    font-size: 13px;
    font-family: 'JetBrains Mono', monospace;
  }

  /* ── SCROLL ANIMATIONS ── */
  .reveal {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity .6s ease, transform .6s ease;
  }
  .reveal.visible { opacity: 1; transform: none; }
</style>
</head>
<body>

<!-- HERO -->
<section class="hero">
  <div class="hero-grid"></div>
  <div class="hero-glow"></div>
  <div class="hero-glow2"></div>

  <div class="badge">
    <span class="badge-dot"></span>
    v1.0 · Python · Telegram Bot API
  </div>

  <h1>
    <span class="line1">TG MEDIA</span>
    <span class="line2">GENERATOR</span>
  </h1>

  <p class="hero-sub">
    Telegram-бот для генерации изображений и видео через бесплатные AI API — Gemini, HuggingFace, Seedance.
  </p>

  <div class="hero-meta">
    <div class="meta-item">
      <span class="meta-val">4</span>
      <span class="meta-label">Модели фото</span>
    </div>
    <div class="meta-item">
      <span class="meta-val">2</span>
      <span class="meta-label">Сервиса видео</span>
    </div>
    <div class="meta-item">
      <span class="meta-val">$0</span>
      <span class="meta-label">Стоимость</span>
    </div>
  </div>
</section>

<!-- MAIN -->
<main class="container">

  <!-- SERVICES -->
  <section class="section reveal">
    <div class="section-label">// сервисы</div>
    <h2>Бесплатные API</h2>
    <div class="services-grid">

      <div class="service-card img">
        <div class="service-icon">✨</div>
        <div class="service-name">Google Gemini</div>
        <div class="service-desc">Лучшее качество изображений. 500 генераций в день без карты.</div>
        <span class="service-tag tag-blue">500/день · бесплатно</span>
      </div>

      <div class="service-card img">
        <div class="service-icon">🎨</div>
        <div class="service-name">Stable Diffusion XL</div>
        <div class="service-desc">Художественный стиль, детализированные сцены. Через HuggingFace.</div>
        <span class="service-tag tag-blue">HuggingFace · бесплатно</span>
      </div>

      <div class="service-card img">
        <div class="service-icon">⚡</div>
        <div class="service-name">Flux Schnell</div>
        <div class="service-desc">Быстрая генерация, универсальный стиль. Black Forest Labs.</div>
        <span class="service-tag tag-blue">HuggingFace · бесплатно</span>
      </div>

      <div class="service-card img">
        <div class="service-icon">📸</div>
        <div class="service-name">Realistic Vision</div>
        <div class="service-desc">Фотореалистичные портреты и сцены. Максимальный реализм.</div>
        <span class="service-tag tag-blue">HuggingFace · бесплатно</span>
      </div>

      <div class="service-card vid">
        <div class="service-icon">🤗</div>
        <div class="service-name">HuggingFace Video</div>
        <div class="service-desc">ModelScope text-to-video. Короткие клипы, полностью бесплатно.</div>
        <span class="service-tag tag-pink">видео · бесплатно</span>
      </div>

      <div class="service-card vid">
        <div class="service-icon">🎬</div>
        <div class="service-name">Seedance 2.0</div>
        <div class="service-desc">Качественное видео 480p–1080p. Бесплатные дневные кредиты.</div>
        <span class="service-tag tag-pink">видео · кредиты/день</span>
      </div>

    </div>
  </section>

  <div class="divider"></div>

  <!-- SETUP -->
  <section class="section reveal">
    <div class="section-label">// установка</div>
    <h2>Быстрый старт</h2>

    <div class="code-block">
      <div class="code-header">
        <div class="code-dots">
          <span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span>
        </div>
        <span class="code-lang">bash</span>
      </div>
      <pre><span class="cmt"># 1. Установи зависимости</span>
<span class="fn">pip</span> install python-telegram-bot requests Pillow

<span class="cmt"># 2. Вставь ключи в CONFIG в bot.py</span>

<span class="cmt"># 3. Запусти</span>
<span class="fn">python</span> bot.py</pre>
    </div>

    <div class="steps">

      <div class="step">
        <div class="step-num">01</div>
        <div class="step-content">
          <div class="step-title">Telegram Bot Token</div>
          <div class="step-desc">Открой @BotFather → /newbot → следуй инструкциям → скопируй токен вида <code>123456:ABCdef...</code></div>
          <a class="step-link" href="https://t.me/BotFather" target="_blank">↗ t.me/BotFather</a>
        </div>
      </div>

      <div class="step">
        <div class="step-num">02</div>
        <div class="step-content">
          <div class="step-title">Google Gemini API Key</div>
          <div class="step-desc">Войди через Google → Get API key → Create API key. Бесплатно, 500 изображений в день, без карты.</div>
          <a class="step-link" href="https://aistudio.google.com" target="_blank">↗ aistudio.google.com</a>
        </div>
      </div>

      <div class="step">
        <div class="step-num">03</div>
        <div class="step-content">
          <div class="step-title">HuggingFace Token</div>
          <div class="step-desc">Зарегистрируйся → Settings → Tokens → New token (тип Read). Токен начинается с <code>hf_...</code></div>
          <a class="step-link" href="https://huggingface.co/settings/tokens" target="_blank">↗ huggingface.co/settings/tokens</a>
        </div>
      </div>

      <div class="step">
        <div class="step-num">04</div>
        <div class="step-content">
          <div class="step-title">Seedance API Key (опционально)</div>
          <div class="step-desc">Войди через Google → скопируй ключ из личного кабинета. Бесплатные дневные кредиты на видео.</div>
          <a class="step-link" href="https://seedanceapi.org" target="_blank">↗ seedanceapi.org</a>
        </div>
      </div>

      <div class="step">
        <div class="step-num">05</div>
        <div class="step-content">
          <div class="step-title">Вставь ключи в bot.py</div>
          <div class="code-block" style="margin-top:12px">
            <div class="code-header">
              <div class="code-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
              <span class="code-lang">python</span>
            </div>
            <pre><span class="var">CONFIG</span> = {
    <span class="str">"TELEGRAM_TOKEN"</span>:   <span class="str">"123456:ABCdef..."</span>,
    <span class="str">"GEMINI_API_KEY"</span>:   <span class="str">"AIzaSy..."</span>,
    <span class="str">"HF_TOKEN"</span>:         <span class="str">"hf_..."</span>,
    <span class="str">"SEEDANCE_API_KEY"</span>: <span class="str">"sk-..."</span>,
}</pre>
          </div>
        </div>
      </div>

    </div>
  </section>

  <div class="divider"></div>

  <!-- DEPLOY -->
  <section class="section reveal">
    <div class="section-label">// деплой</div>
    <h2>Удалённый запуск 24/7</h2>
    <div class="deploy-grid">

      <div class="deploy-card recommended">
        <div class="rec-badge">⭐ Рекомендуем</div>
        <div class="deploy-title">Railway.app</div>
        <div class="deploy-sub">Самый простой способ. Бесплатный тариф, деплой через GitHub.</div>
        <ul class="deploy-steps">
          <li>Загрузи файлы в GitHub репозиторий</li>
          <li>New Project → Deploy from GitHub</li>
          <li>Добавь переменные в Variables</li>
          <li>Бот запустится автоматически</li>
        </ul>
      </div>

      <div class="deploy-card">
        <div class="deploy-title">VPS сервер</div>
        <div class="deploy-sub">Полный контроль. Hetzner / DigitalOcean от $3/мес.</div>
        <ul class="deploy-steps">
          <li>Подключись по SSH</li>
          <li>Запусти <code>bash deploy.sh</code></li>
          <li>Экспортируй переменные окружения</li>
          <li>Запусти <code>bash start.sh</code> (screen)</li>
        </ul>
      </div>

      <div class="deploy-card">
        <div class="deploy-title">Render.com</div>
        <div class="deploy-sub">Бесплатно, но засыпает при неактивности.</div>
        <ul class="deploy-steps">
          <li>New → Background Worker</li>
          <li>Подключи GitHub репо</li>
          <li>Укажи <code>render.yaml</code> конфиг</li>
          <li>Добавь env переменные</li>
        </ul>
      </div>

    </div>

    <div class="code-block" style="margin-top:24px">
      <div class="code-header">
        <div class="code-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
        <span class="code-lang">bash · VPS деплой</span>
      </div>
      <pre><span class="cmt"># Для Railway/Render — переменные окружения (не хардкодить!)</span>
<span class="kw">export</span> <span class="var">TELEGRAM_TOKEN</span>=<span class="str">"твой_токен"</span>
<span class="kw">export</span> <span class="var">GEMINI_API_KEY</span>=<span class="str">"твой_ключ"</span>
<span class="kw">export</span> <span class="var">HF_TOKEN</span>=<span class="str">"hf_..."</span>
<span class="kw">export</span> <span class="var">SEEDANCE_API_KEY</span>=<span class="str">"sk-..."</span>

<span class="cmt"># Запуск в фоне через screen</span>
<span class="fn">screen</span> -dmS tgbot python3 bot.py

<span class="cmt"># Смотреть логи</span>
<span class="fn">screen</span> -r tgbot

<span class="cmt"># Остановить</span>
<span class="fn">screen</span> -S tgbot -X quit</pre>
    </div>
  </section>

  <div class="divider"></div>

  <!-- COMMANDS -->
  <section class="section reveal">
    <div class="section-label">// команды</div>
    <h2>Команды бота</h2>
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:16px;overflow:hidden">
      <table class="cmd-table">
        <thead>
          <tr>
            <th>Команда</th>
            <th>Действие</th>
          </tr>
        </thead>
        <tbody>
          <tr><td><code>/start</code></td><td>Главное меню с выбором режима</td></tr>
          <tr><td><code>/image</code></td><td>Быстрый запуск генерации изображения</td></tr>
          <tr><td><code>/video</code></td><td>Быстрый запуск генерации видео</td></tr>
          <tr><td><code>/help</code></td><td>Справка и советы по промптам</td></tr>
          <tr><td><code>/cancel</code></td><td>Отмена текущей операции</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <div class="divider"></div>

  <!-- TIPS -->
  <section class="section reveal">
    <div class="section-label">// советы</div>
    <h2>Как писать промпты</h2>
    <div class="tips-grid">
      <div class="tip">
        <strong>🇬🇧 Английский язык</strong>
        Все модели обучены на английских данных — результат будет лучше.
      </div>
      <div class="tip">
        <strong>🎨 Указывай стиль</strong>
        photorealistic, anime, oil painting, watercolor, cyberpunk, cinematic...
      </div>
      <div class="tip">
        <strong>💡 Описывай свет</strong>
        golden hour, neon lights, soft shadows, studio lighting...
      </div>
      <div class="tip">
        <strong>📐 Качество</strong>
        Добавляй 4k, ultra detailed, masterpiece, sharp focus в конце промпта.
      </div>
    </div>

    <div class="code-block" style="margin-top:24px">
      <div class="code-header">
        <div class="code-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
        <span class="code-lang">примеры промптов</span>
      </div>
      <pre><span class="cmt"># Изображение — пейзаж</span>
<span class="str">"A misty mountain valley at dawn, volumetric light, photorealistic, 4k"</span>

<span class="cmt"># Изображение — портрет</span>
<span class="str">"Portrait of a woman in red dress, cinematic lighting, sharp focus, film grain"</span>

<span class="cmt"># Видео — природа</span>
<span class="str">"A butterfly landing on a flower in slow motion, macro, golden hour"</span>

<span class="cmt"># Видео — город</span>
<span class="str">"Cyberpunk city street at night, rain, neon reflections, cinematic"</span></pre>
    </div>
  </section>

</main>

<footer>
  TG Media Generator · Python · MIT License · 2025
</footer>

<script>
  // Scroll reveal
  const els = document.querySelectorAll('.reveal');
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); } });
  }, { threshold: 0.1 });
  els.forEach(el => obs.observe(el));
</script>

</body>
</html>
