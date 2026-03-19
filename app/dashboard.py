def get_dashboard_html():
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order Service</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <script>document.documentElement.setAttribute('data-theme',localStorage.getItem('theme')||'light');document.documentElement.classList.add('no-trans');</script>
    <style>
        html.no-trans * { transition: none !important; }
        /* ── Tokens: Light ──────────────────────── */
        :root {
            --primary:        #6366f1;
            --primary-dark:   #4f46e5;
            --primary-light:  #e0e7ff;
            --primary-muted:  #c7d2fe;
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
            --primary-muted:  #312e81;
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
            font-size: 15px;
            line-height: 1.5;
            transition: background var(--transition), color var(--transition);
        }

        /* ── Navbar ─────────────────────────────── */
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

        /* ── Layout ─────────────────────────────── */
        .page { max-width: 1080px; margin: 0 auto; padding: 28px 20px 48px; }

        /* ── Stats ──────────────────────────────── */
        .stats {
            display: grid; grid-template-columns: repeat(4,1fr);
            gap: 14px; margin-bottom: 22px;
        }
        .stat {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 18px 20px;
            box-shadow: var(--shadow); position: relative; overflow: hidden;
            transition: background var(--transition), border-color var(--transition);
        }
        .stat::after {
            content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
        }
        .stat.s-total::after   { background: var(--primary); }
        .stat.s-created::after { background: var(--warning); }
        .stat.s-proc::after    { background: var(--info); }
        .stat.s-done::after    { background: var(--success); }

        .stat-label {
            font-size: 0.75em; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 8px;
        }
        .stat-num {
            font-size: 2em; font-weight: 800; color: var(--text);
            line-height: 1; transition: color var(--transition);
        }

        /* ── Card ───────────────────────────────── */
        .card {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: var(--radius-lg); box-shadow: var(--shadow);
            overflow: hidden; margin-bottom: 18px;
            transition: background var(--transition), border-color var(--transition);
        }
        .card-head {
            padding: 16px 22px;
            display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid var(--border);
        }
        .card-title { font-size: 0.9em; font-weight: 600; color: var(--text); }

        /* ── Buttons ────────────────────────────── */
        .btn {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 8px 16px; border-radius: var(--radius-sm);
            font-size: 0.875em; font-weight: 600; cursor: pointer;
            border: 1px solid transparent; text-decoration: none;
            transition: all 0.18s ease; white-space: nowrap;
        }
        .btn-primary { background: var(--primary); color: #fff; border-color: var(--primary); }
        .btn-primary:hover {
            background: var(--primary-dark); border-color: var(--primary-dark);
            transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99,102,241,0.3);
        }
        .btn-ghost {
            background: transparent; color: var(--text-secondary);
            border-color: var(--border);
        }
        .btn-ghost:hover { background: var(--bg-subtle); color: var(--text); border-color: var(--border-strong); }
        .btn:disabled { opacity: 0.55; pointer-events: none; }

        /* ── Orders ─────────────────────────────── */
        #orders-list { min-height: 120px; }

        .order-row {
            display: flex; align-items: center; gap: 14px;
            padding: 14px 22px; border-bottom: 1px solid var(--border);
            transition: background 0.15s;
        }
        .order-row:last-child { border-bottom: none; }
        .order-row:hover { background: var(--surface-hover); }

        .order-row.is-new { animation: slideIn 0.28s ease; }
        @keyframes slideIn { from{opacity:0;transform:translateY(-6px)} to{opacity:1;transform:none} }

        .order-row.just-created {
            background: var(--success-bg);
            border-left: 3px solid var(--success);
        }
        .order-row.removing {
            opacity: 0; transform: translateX(16px);
            transition: opacity 0.28s ease, transform 0.28s ease;
        }

        .order-icon { font-size: 1.2em; flex-shrink: 0; width: 28px; text-align: center; }
        .order-info { flex: 1; min-width: 0; }
        .order-customer {
            font-weight: 600; font-size: 0.92em;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .order-meta {
            font-size: 0.775em; color: var(--text-muted); margin-top: 2px;
            font-family: 'SF Mono','Fira Code',monospace;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }

        .badge {
            padding: 3px 10px; border-radius: 20px;
            font-size: 0.75em; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.3px;
            white-space: nowrap; flex-shrink: 0;
            transition: background 0.4s ease, color 0.4s ease;
        }
        .badge.b-created    { background: var(--warning-bg);  color: var(--warning); }
        .badge.b-processing { background: var(--info-bg);     color: var(--info); }
        .badge.b-completed  { background: var(--success-bg);  color: var(--success); }
        .badge.b-cancelled  { background: var(--danger-bg);   color: var(--danger); }
        .badge.b-new        { background: var(--success-bg);  color: var(--success); }

        .order-total {
            font-weight: 700; font-size: 0.9em; color: var(--text);
            min-width: 88px; text-align: right; flex-shrink: 0;
        }
        .del-btn {
            width: 30px; height: 30px; border-radius: var(--radius-sm);
            border: 1px solid var(--border); background: transparent;
            color: var(--text-muted); cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.8em; flex-shrink: 0; transition: all 0.18s ease;
        }
        .del-btn:hover {
            background: var(--danger-bg); border-color: var(--danger);
            color: var(--danger); transform: scale(1.1);
        }

        .empty {
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            gap: 10px; padding: 52px 24px;
            color: var(--text-muted); text-align: center;
        }
        .empty-icon { font-size: 2.4em; opacity: 0.45; }
        .empty p { font-size: 0.92em; }

        /* ── Endpoints table ────────────────────── */
        .ep-table { width: 100%; border-collapse: collapse; }
        .ep-table tr {
            border-bottom: 1px solid var(--border);
            transition: background 0.15s;
        }
        .ep-table tr:last-child { border-bottom: none; }
        .ep-table tr:hover { background: var(--surface-hover); }
        .ep-table td {
            padding: 11px 22px; vertical-align: middle; font-size: 0.875em;
        }
        .ep-table td:first-child { width: 60px; }
        .ep-table td:nth-child(2) { width: 230px; }

        .method {
            display: inline-block; padding: 3px 8px; border-radius: 5px;
            font-size: 0.75em; font-weight: 700; font-family: monospace; text-align: center;
        }
        .m-get    { background: var(--success-bg); color: var(--success); }
        .m-post   { background: var(--info-bg);    color: var(--info); }
        .m-patch  { background: var(--warning-bg); color: var(--warning); }
        .m-delete { background: var(--danger-bg);  color: var(--danger); }

        .ep-path {
            font-family: 'SF Mono','Fira Code',monospace;
            font-size: 0.9em; color: var(--text); word-break: break-all;
        }
        .ep-desc { color: var(--text-muted); }

        /* ── Toast ──────────────────────────────── */
        #toasts {
            position: fixed; bottom: 22px; right: 22px;
            display: flex; flex-direction: column; gap: 8px;
            z-index: 999; pointer-events: none;
        }
        .toast {
            display: flex; align-items: center; gap: 9px;
            padding: 11px 16px; border-radius: var(--radius);
            background: var(--surface); border: 1px solid var(--border);
            box-shadow: var(--shadow-lg); font-size: 0.875em; font-weight: 500;
            color: var(--text); min-width: 220px; pointer-events: auto;
            animation: toastIn 0.25s ease;
        }
        .toast.ok  { border-left: 3px solid var(--success); }
        .toast.err { border-left: 3px solid var(--danger); }
        @keyframes toastIn  { from{opacity:0;transform:translateX(14px)} to{opacity:1;transform:none} }
        @keyframes toastOut { from{opacity:1;transform:none} to{opacity:0;transform:translateX(14px)} }

        .spin {
            width: 13px; height: 13px;
            border: 2px solid var(--border); border-top-color: var(--primary);
            border-radius: 50%; animation: spinning 0.6s linear infinite; flex-shrink: 0;
        }
        @keyframes spinning { to{transform:rotate(360deg)} }

        /* ── Language selector ──────────────────── */
        .lang-selector {
            position: relative;
            margin-left: 4px;
        }
        .lang-toggle {
            display: flex; align-items: center; gap: 6px;
            padding: 5px 10px; border-radius: var(--radius-sm);
            border: 1px solid var(--border); background: var(--surface);
            color: var(--text-secondary); cursor: pointer;
            font-size: 0.85em; font-weight: 600;
            transition: background var(--transition), border-color var(--transition);
        }
        .lang-toggle:hover {
            background: var(--bg-subtle); border-color: var(--border-strong);
        }
        .lang-arrow {
            font-size: 0.7em; opacity: 0.6;
            transition: transform 0.2s;
        }
        .lang-selector.open .lang-arrow { transform: rotate(180deg); }
        .lang-menu {
            display: none;
            position: absolute; top: calc(100% + 4px); right: 0;
            background: var(--surface); border: 1px solid var(--border);
            border-radius: var(--radius); box-shadow: var(--shadow-lg);
            min-width: 160px; overflow: hidden; z-index: 300;
        }
        .lang-selector.open .lang-menu { display: block; }
        .lang-option {
            display: flex; align-items: center; gap: 8px; width: 100%;
            padding: 10px 14px; border: none; background: none;
            color: var(--text); font-size: 0.88em; cursor: pointer;
            transition: background 0.15s;
        }
        .lang-option:hover { background: var(--bg-subtle); }
        .lang-check {
            margin-left: auto; color: var(--primary); font-weight: 700;
        }

        /* ── Footer ─────────────────────────────── */
        footer {
            text-align: center;
            padding: 24px 20px 32px;
            color: var(--text-muted);
            font-size: 0.8em;
            border-top: 1px solid var(--border);
            margin-top: 8px;
        }

        @media (max-width: 760px) {
            .stats { grid-template-columns: 1fr 1fr; }
            .ep-table td:nth-child(3) { display: none; }
            nav { padding: 0 16px; }
            .page { padding: 16px 12px 40px; }
        }
        @media (max-width: 480px) {
            .order-meta, .order-total { display: none; }
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
            <span data-i18n="nav.operational">Operacional</span>
        </div>
        <div class="nav-divider"></div>
        <a class="nav-link active" href="/" data-i18n="nav.home">Dashboard</a>
        <a class="nav-link" href="/docs" data-i18n="nav.docs">Docs</a>
        <a class="nav-link" href="/metrics">Metrics</a>
        <a class="nav-link" href="/health">Health</a>
        <div class="lang-selector" id="lang-selector">
            <button class="lang-toggle" id="lang-toggle" onclick="toggleLangMenu()">
                <span id="lang-flag">🇧🇷</span>
                <span id="lang-label">PT</span>
                <span class="lang-arrow">▾</span>
            </button>
            <div class="lang-menu" id="lang-menu">
                <button class="lang-option" onclick="selectLang('pt')">
                    <span>🇧🇷</span> Português
                    <span class="lang-check" id="check-pt">✓</span>
                </button>
                <button class="lang-option" onclick="selectLang('en')">
                    <span>🇺🇸</span> English
                    <span class="lang-check" id="check-en"></span>
                </button>
            </div>
        </div>
        <button class="icon-btn" id="theme-btn" title="Tema / Theme" onclick="toggleTheme()">🌙</button>
    </div>
</nav>

<div class="page">

    <div class="stats">
        <div class="stat s-total">
            <div class="stat-label" data-i18n="stat.total">Total</div>
            <div class="stat-num" id="s-total">—</div>
        </div>
        <div class="stat s-created">
            <div class="stat-label" data-i18n="stat.created">Criados</div>
            <div class="stat-num" id="s-created">—</div>
        </div>
        <div class="stat s-proc">
            <div class="stat-label" data-i18n="stat.processing">Processando</div>
            <div class="stat-num" id="s-proc">—</div>
        </div>
        <div class="stat s-done">
            <div class="stat-label" data-i18n="stat.completed">Concluídos</div>
            <div class="stat-num" id="s-done">—</div>
        </div>
    </div>

    <div class="card">
        <div class="card-head">
            <span class="card-title" data-i18n="orders.title">Pedidos</span>
            <div style="display:flex;gap:8px;">
                <button class="btn btn-ghost" onclick="refresh()">
                    ↺ <span data-i18n="btn.refresh">Atualizar</span>
                </button>
                <button class="btn btn-primary" id="btn-new" onclick="createOrder()">
                    ＋ <span data-i18n="btn.create">Criar Pedido Teste</span>
                </button>
            </div>
        </div>
        <div id="orders-list">
            <div class="empty">
                <div class="spin"></div>
                <p data-i18n="loading">Carregando…</p>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-head">
            <span class="card-title" data-i18n="ep.title">Endpoints da API</span>
            <a class="btn btn-ghost" href="/docs" style="font-size:0.82em;padding:5px 12px;" data-i18n="ep.open">Abrir Docs →</a>
        </div>
        <table class="ep-table">
            <tr>
                <td><span class="method m-get">GET</span></td>
                <td><span class="ep-path">/health</span></td>
                <td class="ep-desc" data-i18n="ep.health">Health check da aplicação</td>
            </tr>
            <tr>
                <td><span class="method m-get">GET</span></td>
                <td><span class="ep-path">/metrics</span></td>
                <td class="ep-desc" data-i18n="ep.metrics">Métricas Prometheus</td>
            </tr>
            <tr>
                <td><span class="method m-post">POST</span></td>
                <td><span class="ep-path">/orders</span></td>
                <td class="ep-desc" data-i18n="ep.create">Criar novo pedido</td>
            </tr>
            <tr>
                <td><span class="method m-get">GET</span></td>
                <td><span class="ep-path">/orders</span></td>
                <td class="ep-desc" data-i18n="ep.list">Listar todos os pedidos</td>
            </tr>
            <tr>
                <td><span class="method m-get">GET</span></td>
                <td><span class="ep-path">/orders/{id}</span></td>
                <td class="ep-desc" data-i18n="ep.get">Buscar pedido por ID</td>
            </tr>
            <tr>
                <td><span class="method m-patch">PATCH</span></td>
                <td><span class="ep-path">/orders/{id}/status</span></td>
                <td class="ep-desc" data-i18n="ep.update">Atualizar status</td>
            </tr>
            <tr>
                <td><span class="method m-delete">DELETE</span></td>
                <td><span class="ep-path">/orders/{id}</span></td>
                <td class="ep-desc" data-i18n="ep.cancel">Cancelar pedido</td>
            </tr>
        </table>
    </div>

</div>

<footer>Desenvolvido por <strong>Matheus Santos Caldas</strong></footer>

<div id="toasts"></div>

<script>
const BASE = window.location.origin;

// ── i18n ─────────────────────────────────
const TR = {
    pt: {
        'nav.home':        'Dashboard',
        'nav.operational': 'Operacional',
        'nav.docs':        'Docs',
        'stat.total':      'Total',
        'stat.created':    'Criados',
        'stat.processing': 'Processando',
        'stat.completed':  'Concluídos',
        'orders.title':    'Pedidos',
        'btn.refresh':     'Atualizar',
        'btn.create':      'Criar Pedido Teste',
        'btn.creating':    'Criando…',
        'loading':         'Carregando…',
        'ep.title':        'Endpoints da API',
        'ep.open':         'Abrir Docs →',
        'ep.health':       'Health check da aplicação',
        'ep.metrics':      'Métricas Prometheus',
        'ep.create':       'Criar novo pedido',
        'ep.list':         'Listar todos os pedidos',
        'ep.get':          'Buscar pedido por ID',
        'ep.update':       'Atualizar status',
        'ep.cancel':       'Cancelar pedido',
        'status.created':    'Criado',
        'status.processing': 'Processando',
        'status.completed':  'Concluído',
        'status.cancelled':  'Cancelado',
        'status.new':        '✓ Criado',
        'empty.text':    'Nenhum pedido ainda',
        'empty.btn':     '＋ Criar primeiro pedido',
        'toast.created': 'Pedido criado!',
        'toast.deleted': 'Pedido cancelado.',
        'toast.refresh': 'Atualizado.',
        'toast.err.create': 'Erro ao criar pedido.',
        'toast.err.delete': 'Erro ao cancelar pedido.',
    },
    en: {
        'nav.home':        'Dashboard',
        'nav.operational': 'Operational',
        'nav.docs':        'Docs',
        'stat.total':      'Total',
        'stat.created':    'Created',
        'stat.processing': 'Processing',
        'stat.completed':  'Completed',
        'orders.title':    'Orders',
        'btn.refresh':     'Refresh',
        'btn.create':      'Create Test Order',
        'btn.creating':    'Creating…',
        'loading':         'Loading…',
        'ep.title':        'API Endpoints',
        'ep.open':         'Open Docs →',
        'ep.health':       'Application health check',
        'ep.metrics':      'Prometheus metrics',
        'ep.create':       'Create a new order',
        'ep.list':         'List all orders',
        'ep.get':          'Get order by ID',
        'ep.update':       'Update status',
        'ep.cancel':       'Cancel order',
        'status.created':    'Created',
        'status.processing': 'Processing',
        'status.completed':  'Completed',
        'status.cancelled':  'Cancelled',
        'status.new':        '✓ Created',
        'empty.text':    'No orders yet',
        'empty.btn':     '＋ Create first order',
        'toast.created': 'Order created!',
        'toast.deleted': 'Order cancelled.',
        'toast.refresh': 'Refreshed.',
        'toast.err.create': 'Failed to create order.',
        'toast.err.delete': 'Failed to cancel order.',
    },
};

const ICONS = { created:'🟡', processing:'🔵', completed:'🟢', cancelled:'🔴' };
const BADGE = { created:'b-created', processing:'b-processing', completed:'b-completed', cancelled:'b-cancelled' };

let currentLang = localStorage.getItem('lang') || 'pt';
let currentTheme = localStorage.getItem('theme') || 'light';
let LABELS = {};

function t(key) { return TR[currentLang][key] ?? TR['pt'][key] ?? key; }

function applyLang(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    LABELS = {
        created:    t('status.created'),
        processing: t('status.processing'),
        completed:  t('status.completed'),
        cancelled:  t('status.cancelled'),
    };
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const k = el.getAttribute('data-i18n');
        el.textContent = t(k);
    });
    // Update lang selector
    const flag = document.getElementById('lang-flag');
    const label = document.getElementById('lang-label');
    if (flag) flag.textContent = lang === 'pt' ? '🇧🇷' : '🇺🇸';
    if (label) label.textContent = lang === 'pt' ? 'PT' : 'EN';
    document.getElementById('check-pt').textContent = lang === 'pt' ? '✓' : '';
    document.getElementById('check-en').textContent = lang === 'en' ? '✓' : '';
    // force re-render to update dynamic status labels
    ordersCache = null;
    loadOrders();
}

function toggleLangMenu() {
    document.getElementById('lang-selector').classList.toggle('open');
}
function selectLang(lang) {
    applyLang(lang);
    document.getElementById('lang-selector').classList.remove('open');
}
document.addEventListener('click', (e) => {
    const sel = document.getElementById('lang-selector');
    if (sel && !sel.contains(e.target)) sel.classList.remove('open');
});

// ── Theme ─────────────────────────────────
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

// ── Toast ─────────────────────────────────
function toast(msg, type = 'ok') {
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<span>${type === 'ok' ? '✓' : '✗'}</span> ${msg}`;
    document.getElementById('toasts').appendChild(el);
    setTimeout(() => {
        el.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => el.remove(), 300);
    }, 3000);
}

// ── Stats ─────────────────────────────────
function updateStats(orders) {
    const s = (id, v) => { const el=document.getElementById(id); if(el) el.textContent=v; };
    s('s-total',   orders.length);
    s('s-created', orders.filter(o=>o.status==='created').length);
    s('s-proc',    orders.filter(o=>o.status==='processing').length);
    s('s-done',    orders.filter(o=>o.status==='completed').length);
}

// ── Build row ─────────────────────────────
function buildRow(order, isNew = false) {
    const row = document.createElement('div');
    row.className = `order-row${isNew ? ' just-created is-new' : ''}`;
    row.id = `o-${order.id}`;
    row.dataset.id = order.id;
    row.dataset.status = order.status;

    row.innerHTML = `
        <div class="order-icon">${ICONS[order.status] ?? '⚪'}</div>
        <div class="order-info">
            <div class="order-customer">${order.customer}</div>
            <div class="order-meta">#${order.id.substring(0,8)} · ${order.items.join(', ')}</div>
        </div>
        <span class="badge ${isNew ? 'b-new' : BADGE[order.status]}">
            ${isNew ? t('status.new') : LABELS[order.status]}
        </span>
        <div class="order-total">R$ ${order.total.toFixed(2)}</div>
        <button class="del-btn" title="${t('ep.cancel')}" onclick="deleteOrder('${order.id}')">✕</button>`;

    if (isNew) {
        setTimeout(() => {
            row.style.transition = 'background 0.9s ease, border-left 0.9s ease';
            row.classList.remove('just-created');
            const badge = row.querySelector('.badge');
            if (badge) {
                badge.style.transition = 'background 0.6s ease, color 0.6s ease';
                badge.className = `badge ${BADGE[order.status]}`;
                badge.textContent = LABELS[order.status];
            }
        }, 2500);
    }
    return row;
}

function emptyHTML() {
    return `<div class="empty">
        <div class="empty-icon">📭</div>
        <p>${t('empty.text')}</p>
        <button class="btn btn-primary" style="margin-top:8px;" onclick="createOrder()">
            ${t('empty.btn')}
        </button>
    </div>`;
}

// ── Smart render ──────────────────────────
let ordersCache = null;
let lastNewId   = null;

function smartRender(orders) {
    const list = document.getElementById('orders-list');
    const reversed = [...orders].reverse();

    if (ordersCache === null) {
        list.innerHTML = orders.length === 0 ? emptyHTML() : '';
        if (orders.length > 0) reversed.forEach(o => list.appendChild(buildRow(o, false)));
        ordersCache = orders;
        updateStats(orders);
        return;
    }

    const oldMap = new Map(ordersCache.map(o => [o.id, o]));
    const newMap = new Map(orders.map(o => [o.id, o]));
    const hasChanges =
        orders.length !== ordersCache.length ||
        orders.some(o => { const old = oldMap.get(o.id); return !old || old.status !== o.status; });
    if (!hasChanges) return;

    ordersCache = orders;

    oldMap.forEach((_, id) => {
        if (!newMap.has(id)) {
            const el = document.getElementById(`o-${id}`);
            if (el) { el.classList.add('removing'); setTimeout(() => el.remove(), 300); }
        }
    });

    if (orders.length === 0) {
        setTimeout(() => { list.innerHTML = emptyHTML(); }, 300);
        updateStats(orders); return;
    }

    const emptyEl = list.querySelector('.empty');
    if (emptyEl) list.innerHTML = '';

    reversed.forEach(order => {
        const existing = document.getElementById(`o-${order.id}`);
        if (existing) {
            if (existing.dataset.status !== order.status) {
                existing.dataset.status = order.status;
                const icon  = existing.querySelector('.order-icon');
                const badge = existing.querySelector('.badge');
                if (icon)  icon.textContent = ICONS[order.status];
                if (badge) { badge.className = `badge ${BADGE[order.status]}`; badge.textContent = LABELS[order.status]; }
            }
        } else {
            const isNew = order.id === lastNewId;
            const row = buildRow(order, isNew);
            list.insertBefore(row, list.querySelector('.order-row') || null);
        }
    });
    updateStats(orders);
}

// ── Load ──────────────────────────────────
async function loadOrders() {
    try {
        const res = await fetch(`${BASE}/orders`);
        if (!res.ok) return;
        smartRender(await res.json());
    } catch { /* silent */ }
}

async function refresh() {
    ordersCache = null;
    await loadOrders();
    toast(t('toast.refresh'));
}

// ── Create ────────────────────────────────
const CUSTOMERS = ['João Silva','Maria Santos','Pedro Costa','Ana Oliveira','Carlos Souza','Beatriz Lima'];
const ITEMS_LIST = [
    ['Notebook Pro','Mouse Gamer'],['Teclado Mecânico','Monitor 27"'],
    ['Webcam Full HD','Headset BT'],['SSD NVMe 1TB','Hub USB-C'],
    ['Mousepad XL','Suporte Notebook'],['Cadeira Gamer','Mesa Articulada'],
];

async function createOrder() {
    const btn = document.getElementById('btn-new');
    const span = btn.querySelector('[data-i18n="btn.create"]');
    btn.disabled = true;
    if (span) span.textContent = t('btn.creating');

    const customer = CUSTOMERS[Math.floor(Math.random() * CUSTOMERS.length)];
    const items    = ITEMS_LIST[Math.floor(Math.random() * ITEMS_LIST.length)];
    const total    = parseFloat((Math.random() * 1500 + 80).toFixed(2));

    try {
        const res = await fetch(`${BASE}/orders`, {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({customer, items, total}),
        });
        if (!res.ok) throw new Error();
        const order = await res.json();
        lastNewId = order.id;
        ordersCache = null;
        await loadOrders();
        toast(t('toast.created'));
    } catch {
        toast(t('toast.err.create'), 'err');
    } finally {
        btn.disabled = false;
        if (span) span.textContent = t('btn.create');
    }
}

// ── Delete ────────────────────────────────
async function deleteOrder(id) {
    const el = document.getElementById(`o-${id}`);
    if (el) el.classList.add('removing');
    try {
        const res = await fetch(`${BASE}/orders/${id}`, {method:'DELETE'});
        if (!res.ok) throw new Error();
        await new Promise(r => setTimeout(r, 300));
        ordersCache = null;
        await loadOrders();
        toast(t('toast.deleted'));
    } catch {
        if (el) el.classList.remove('removing');
        toast(t('toast.err.delete'), 'err');
    }
}

// ── Init ──────────────────────────────────
applyTheme(currentTheme);
applyLang(currentLang);
requestAnimationFrame(() => document.documentElement.classList.remove('no-trans'));
setInterval(loadOrders, 8000);
</script>
</body>
</html>"""
