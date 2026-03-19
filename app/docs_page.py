def get_docs_html() -> str:
    return """<!DOCTYPE html>
<html data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Docs — Order Service</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
        /* ── Tokens: Light ──────────────────────── */
        :root {
            --primary:        #6366f1;
            --primary-dark:   #4f46e5;
            --primary-light:  #e0e7ff;
            --success:        #10b981;
            --success-bg:     #d1fae5;
            --warning:        #f59e0b;
            --warning-bg:     #fef3c7;
            --info:           #0ea5e9;
            --info-bg:        #e0f2fe;
            --danger:         #ef4444;
            --danger-bg:      #fee2e2;
            --bg:             #f1f5f9;
            --bg-subtle:      #e8edf4;
            --surface:        #ffffff;
            --surface-hover:  #f8fafc;
            --border:         #e2e8f0;
            --border-strong:  #cbd5e1;
            --text:           #0f172a;
            --text-secondary: #475569;
            --text-muted:     #94a3b8;
            --radius-sm: 6px;
            --radius:    10px;
            --radius-lg: 14px;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
            --shadow:    0 1px 3px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.04);
            --shadow-lg: 0 8px 30px rgba(0,0,0,0.10);
            --nav-height: 60px;
            --transition: 0.2s ease;
        }
        /* ── Tokens: Dark ───────────────────────── */
        [data-theme="dark"] {
            --primary:        #818cf8;
            --primary-dark:   #6366f1;
            --primary-light:  #1e1b4b;
            --success:        #34d399;
            --success-bg:     #064e3b;
            --warning:        #fbbf24;
            --warning-bg:     #78350f;
            --info:           #38bdf8;
            --info-bg:        #0c4a6e;
            --danger:         #f87171;
            --danger-bg:      #7f1d1d;
            --bg:             #0f172a;
            --bg-subtle:      #1a2236;
            --surface:        #1e293b;
            --surface-hover:  #263348;
            --border:         #334155;
            --border-strong:  #475569;
            --text:           #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted:     #64748b;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
            --shadow:    0 1px 3px rgba(0,0,0,0.3), 0 4px 16px rgba(0,0,0,0.2);
            --shadow-lg: 0 8px 30px rgba(0,0,0,0.4);
        }

        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            transition: background var(--transition), color var(--transition);
        }

        /* ── Navbar (identical to dashboard) ───── */
        nav {
            position: sticky; top: 0; z-index: 200;
            height: var(--nav-height);
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
            display: flex; align-items: center; padding: 0 28px; gap: 16px;
            transition: background var(--transition), border-color var(--transition);
        }
        .nav-brand {
            display: flex; align-items: center; gap: 9px;
            font-weight: 700; font-size: 1.05em;
            color: var(--primary); text-decoration: none;
        }
        .nav-logo {
            width: 30px; height: 30px; border-radius: var(--radius-sm);
            background: linear-gradient(135deg, var(--primary), #8b5cf6);
            display: flex; align-items: center; justify-content: center;
            font-size: 0.95em; flex-shrink: 0;
        }
        .nav-links {
            display: flex; align-items: center; gap: 2px; margin-left: auto;
        }
        .nav-link {
            padding: 6px 12px; border-radius: var(--radius-sm);
            text-decoration: none; color: var(--text-secondary);
            font-size: 0.88em; font-weight: 500;
            transition: background var(--transition), color var(--transition);
        }
        .nav-link:hover { background: var(--primary-light); color: var(--primary); }
        .nav-link.active { background: var(--primary-light); color: var(--primary); }
        .nav-divider { width: 1px; height: 20px; background: var(--border); margin: 0 6px; }
        .nav-status {
            display: flex; align-items: center; gap: 6px;
            font-size: 0.82em; font-weight: 500; color: var(--success);
            padding: 5px 10px; background: var(--success-bg); border-radius: 20px;
        }
        .pulse-dot {
            width: 7px; height: 7px; border-radius: 50%;
            background: var(--success); animation: pulse 2.4s ease-in-out infinite;
        }
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.85)} }
        .icon-btn {
            width: 34px; height: 34px; border-radius: var(--radius-sm);
            border: 1px solid var(--border); background: var(--surface);
            color: var(--text-secondary); cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.9em; font-weight: 700;
            transition: background var(--transition), border-color var(--transition), transform 0.15s;
            margin-left: 4px;
        }
        .icon-btn:hover {
            background: var(--bg-subtle); border-color: var(--border-strong);
            transform: scale(1.08);
        }

        /* ── Swagger container ──────────────────── */
        #swagger-ui {
            max-width: 1080px;
            margin: 0 auto;
            padding: 24px 20px 48px;
        }

        /* ── Swagger UI: hide default topbar ────── */
        .swagger-ui .topbar { display: none !important; }

        /* ── Swagger UI: Light theme polish ─────── */
        .swagger-ui { color: var(--text); }

        .swagger-ui .info { margin-bottom: 8px; }
        .swagger-ui .info .title {
            color: var(--text) !important;
            font-family: inherit !important;
        }
        .swagger-ui .info p,
        .swagger-ui .info li,
        .swagger-ui .info a { color: var(--text-secondary) !important; }

        .swagger-ui .scheme-container {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
            box-shadow: var(--shadow) !important;
            padding: 14px 16px !important;
            margin: 12px 0 !important;
        }

        /* Operation blocks */
        .swagger-ui .opblock {
            border-radius: var(--radius) !important;
            margin-bottom: 8px !important;
            box-shadow: var(--shadow-sm) !important;
        }
        .swagger-ui .opblock-summary {
            border-radius: var(--radius) !important;
            padding: 10px 14px !important;
        }
        .swagger-ui .opblock.opblock-get    { border-color: var(--success) !important; background: var(--success-bg) !important; }
        .swagger-ui .opblock.opblock-post   { border-color: var(--info)    !important; background: var(--info-bg)    !important; }
        .swagger-ui .opblock.opblock-patch  { border-color: var(--warning) !important; background: var(--warning-bg) !important; }
        .swagger-ui .opblock.opblock-delete { border-color: var(--danger)  !important; background: var(--danger-bg)  !important; }

        .swagger-ui .opblock-tag {
            border-color: var(--border) !important;
            font-family: inherit !important;
            font-size: 1em !important;
            font-weight: 700 !important;
            color: var(--text) !important;
            padding: 8px 0 !important;
        }
        .swagger-ui .opblock-tag:hover { background: var(--surface-hover) !important; }
        .swagger-ui .opblock-tag small { color: var(--text-muted) !important; }

        .swagger-ui .opblock-summary-description { color: var(--text-secondary) !important; }
        .swagger-ui .opblock-summary-path { font-family: 'SF Mono','Fira Code',monospace !important; }

        /* Execute button */
        .swagger-ui .btn.execute {
            background: var(--primary) !important;
            border-color: var(--primary) !important;
            color: #fff !important;
            border-radius: var(--radius-sm) !important;
            font-family: inherit !important;
            font-weight: 600 !important;
        }
        .swagger-ui .btn.execute:hover {
            background: var(--primary-dark) !important;
            border-color: var(--primary-dark) !important;
        }
        .swagger-ui .btn.cancel {
            border-radius: var(--radius-sm) !important;
        }
        .swagger-ui .btn.authorize {
            border-radius: var(--radius-sm) !important;
            color: var(--primary) !important;
            border-color: var(--primary) !important;
        }

        /* Models section */
        .swagger-ui section.models {
            border-radius: var(--radius) !important;
            border-color: var(--border) !important;
        }
        .swagger-ui section.models h4 {
            font-family: inherit !important;
            color: var(--text) !important;
        }

        /* ── Swagger UI: Dark theme overrides ───── */
        [data-theme="dark"] .swagger-ui .wrapper { background: transparent !important; }
        [data-theme="dark"] .swagger-ui { color: var(--text) !important; }

        /* Info */
        [data-theme="dark"] .swagger-ui .info .title { color: var(--text) !important; }
        [data-theme="dark"] .swagger-ui .info p,
        [data-theme="dark"] .swagger-ui .info li { color: var(--text-secondary) !important; }
        [data-theme="dark"] .swagger-ui .info .base-url { color: var(--text-muted) !important; }

        /* Operation tag */
        [data-theme="dark"] .swagger-ui .opblock-tag { color: var(--text) !important; border-color: var(--border) !important; }
        [data-theme="dark"] .swagger-ui .opblock-tag:hover { background: var(--surface-hover) !important; }
        [data-theme="dark"] .swagger-ui .opblock-tag small { color: var(--text-muted) !important; }

        /* Operation summary text */
        [data-theme="dark"] .swagger-ui .opblock-summary-description { color: var(--text) !important; }
        [data-theme="dark"] .swagger-ui .opblock-summary-path__deprecated { color: var(--danger) !important; }

        /* Expanded body */
        [data-theme="dark"] .swagger-ui .opblock-body { background: var(--bg-subtle) !important; }
        [data-theme="dark"] .swagger-ui .opblock-section-header {
            background: var(--surface) !important;
            border-color: var(--border) !important;
        }
        [data-theme="dark"] .swagger-ui .opblock-section-header h4,
        [data-theme="dark"] .swagger-ui .opblock-section-header label { color: var(--text) !important; }

        /* Parameters */
        [data-theme="dark"] .swagger-ui table thead tr th,
        [data-theme="dark"] .swagger-ui table thead tr td { color: var(--text-secondary) !important; border-color: var(--border) !important; }
        [data-theme="dark"] .swagger-ui .parameter__name,
        [data-theme="dark"] .swagger-ui .parameter__type,
        [data-theme="dark"] .swagger-ui .parameter__in,
        [data-theme="dark"] .swagger-ui .parameters-col_description p { color: var(--text) !important; }
        [data-theme="dark"] .swagger-ui .parameter__deprecated { color: var(--danger) !important; }

        /* Inputs */
        [data-theme="dark"] .swagger-ui input[type=text],
        [data-theme="dark"] .swagger-ui input[type=password],
        [data-theme="dark"] .swagger-ui input[type=search],
        [data-theme="dark"] .swagger-ui textarea,
        [data-theme="dark"] .swagger-ui select {
            background: var(--bg-subtle) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
        }

        /* Responses */
        [data-theme="dark"] .swagger-ui .responses-inner { background: var(--bg) !important; }
        [data-theme="dark"] .swagger-ui .response-col_status,
        [data-theme="dark"] .swagger-ui .response-col_description p { color: var(--text) !important; }
        [data-theme="dark"] .swagger-ui .response-col_links { color: var(--text-muted) !important; }

        /* Code blocks */
        [data-theme="dark"] .swagger-ui .microlight {
            background: var(--bg-subtle) !important;
            color: #e2e8f0 !important;
        }
        [data-theme="dark"] .swagger-ui .highlight-code > .microlight {
            background: #1a2236 !important;
        }

        /* Models */
        [data-theme="dark"] .swagger-ui section.models {
            background: var(--surface) !important;
            border-color: var(--border) !important;
        }
        [data-theme="dark"] .swagger-ui section.models h4 { color: var(--text) !important; }
        [data-theme="dark"] .swagger-ui .model-box { background: var(--bg-subtle) !important; }
        [data-theme="dark"] .swagger-ui .model { color: var(--text-secondary) !important; }
        [data-theme="dark"] .swagger-ui .model-title { color: var(--text) !important; }
        [data-theme="dark"] .swagger-ui span.prop-name { color: var(--primary) !important; }
        [data-theme="dark"] .swagger-ui span.prop-type { color: var(--info) !important; }
        [data-theme="dark"] .swagger-ui .prop-format { color: var(--warning) !important; }

        /* Scheme container */
        [data-theme="dark"] .swagger-ui .scheme-container { background: var(--surface) !important; box-shadow: var(--shadow) !important; }
        [data-theme="dark"] .swagger-ui .servers > label { color: var(--text) !important; }
        [data-theme="dark"] .swagger-ui .servers > label select {
            background: var(--bg-subtle) !important;
            color: var(--text) !important;
            border-color: var(--border) !important;
        }

        /* Auth modal */
        [data-theme="dark"] .swagger-ui .dialog-ux .modal-ux {
            background: var(--surface) !important;
            border-color: var(--border) !important;
        }
        [data-theme="dark"] .swagger-ui .dialog-ux .modal-ux-header {
            border-color: var(--border) !important;
        }
        [data-theme="dark"] .swagger-ui .dialog-ux .modal-ux-header h3,
        [data-theme="dark"] .swagger-ui .dialog-ux .modal-ux-content p,
        [data-theme="dark"] .swagger-ui .dialog-ux .modal-ux-content label { color: var(--text) !important; }

        /* Buttons in dark */
        [data-theme="dark"] .swagger-ui .btn { color: var(--text) !important; border-color: var(--border) !important; background: var(--surface) !important; }
        [data-theme="dark"] .swagger-ui .btn.execute { color: #fff !important; background: var(--primary) !important; border-color: var(--primary) !important; }
        [data-theme="dark"] .swagger-ui .btn.authorize { color: var(--primary) !important; border-color: var(--primary) !important; background: transparent !important; }

        /* Loading */
        [data-theme="dark"] .swagger-ui .loading-container .loading::after { color: var(--text-muted) !important; }

        @media (max-width: 768px) {
            nav { padding: 0 16px; }
            #swagger-ui { padding: 16px 12px 40px; }
        }
    </style>
</head>
<body>

<nav>
    <a class="nav-brand" href="/">
        <div class="nav-logo">📦</div>
        Order Service
    </a>
    <div class="nav-links">
        <div class="nav-status">
            <div class="pulse-dot"></div>
            <span id="nav-status-text">Operacional</span>
        </div>
        <div class="nav-divider"></div>
        <a class="nav-link" href="/" id="nav-home">Dashboard</a>
        <a class="nav-link active" href="/docs" id="nav-docs">Docs</a>
        <a class="nav-link" href="/metrics">Metrics</a>
        <a class="nav-link" href="/health">Health</a>
        <button class="icon-btn" id="lang-btn" title="Idioma / Language" onclick="toggleLang()">EN</button>
        <button class="icon-btn" id="theme-btn" title="Tema / Theme" onclick="toggleTheme()">🌙</button>
    </div>
</nav>

<div id="swagger-ui"></div>

<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
    // ── i18n ───────────────────────────────
    const DOCS_TR = {
        pt: {
            'nav.home':        'Dashboard',
            'nav.docs':        'Docs',
            'nav.operational': 'Operacional',
        },
        en: {
            'nav.home':        'Dashboard',
            'nav.docs':        'Docs',
            'nav.operational': 'Operational',
        },
    };

    let currentLang  = localStorage.getItem('lang')  || 'pt';
    let currentTheme = localStorage.getItem('theme') || 'light';

    function t(key) { return DOCS_TR[currentLang][key] ?? key; }

    function applyLang(lang) {
        currentLang = lang;
        localStorage.setItem('lang', lang);
        document.getElementById('lang-btn').textContent  = lang === 'pt' ? 'EN' : 'PT';
        document.getElementById('nav-status-text').textContent = t('nav.operational');
        document.getElementById('nav-home').textContent = t('nav.home');
        document.getElementById('nav-docs').textContent = t('nav.docs');
    }

    function toggleLang() { applyLang(currentLang === 'pt' ? 'en' : 'pt'); }

    // ── Theme ──────────────────────────────
    function applyTheme(theme) {
        currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        document.getElementById('theme-btn').textContent = theme === 'dark' ? '☀️' : '🌙';
        localStorage.setItem('theme', theme);
    }
    function toggleTheme() { applyTheme(currentTheme === 'dark' ? 'light' : 'dark'); }

    // Cross-tab sync
    window.addEventListener('storage', e => {
        if (e.key === 'theme' && e.newValue) applyTheme(e.newValue);
        if (e.key === 'lang'  && e.newValue) applyLang(e.newValue);
    });

    // ── Init ───────────────────────────────
    applyTheme(currentTheme);
    applyLang(currentLang);

    // ── Swagger UI ─────────────────────────
    SwaggerUIBundle({
        url:     '/openapi.json',
        dom_id:  '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout:  'BaseLayout',
        deepLinking:           true,
        docExpansion:          'list',
        defaultModelsExpandDepth: -1,
        displayRequestDuration: true,
    });
</script>
</body>
</html>"""
