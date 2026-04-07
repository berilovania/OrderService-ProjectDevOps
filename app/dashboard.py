def get_dashboard_html():
    return """<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Order Service</title>
  <link rel="icon" href="/favicon.ico" type="image/x-icon">
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
      background: #0f172a;
      color: #f1f5f9;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 48px 56px;
      text-align: center;
      max-width: 420px;
      width: 100%;
    }
    h1 { font-size: 1.6rem; font-weight: 700; margin-bottom: 8px; }
    .version { font-size: 0.85rem; color: #64748b; margin-bottom: 32px; }
    .links { display: flex; flex-direction: column; gap: 12px; }
    a {
      display: block;
      padding: 12px 20px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 500;
      font-size: 0.95rem;
      transition: opacity 0.15s;
    }
    a:hover { opacity: 0.85; }
    .btn-primary { background: #6366f1; color: #fff; }
    .btn-secondary {
      background: transparent;
      color: #94a3b8;
      border: 1px solid #334155;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Order Service</h1>
    <p class="version">v2.0.0 &mdash; DevOps Showcase</p>
    <div class="links">
      <a class="btn-primary" href="/grafana">Ver Métricas no Grafana</a>
      <a class="btn-secondary" href="/docs">Documentação da API</a>
      <a class="btn-secondary" href="/health">Health Check</a>
    </div>
  </div>
</body>
</html>"""
