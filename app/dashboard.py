from .routes import orders


def get_dashboard_html():
    return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order Service — Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            background: white;
            padding: 40px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            text-align: center;
        }

        h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
        }

        .status-badge {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 10px;
            font-size: 0.9em;
            font-weight: 600;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }

        .stat-label {
            color: #666;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .endpoints {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .endpoint {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }

        .endpoint-method {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85em;
            margin-bottom: 8px;
        }

        .method-get { background: #d1fae5; color: #059669; }
        .method-post { background: #dbeafe; color: #0369a1; }
        .method-patch { background: #fef3c7; color: #b45309; }
        .method-delete { background: #fee2e2; color: #dc2626; }

        .endpoint-path {
            font-family: 'Monaco', 'Courier New', monospace;
            color: #333;
            font-size: 0.9em;
            margin: 8px 0;
        }

        .endpoint-description {
            color: #666;
            font-size: 0.85em;
            margin-top: 8px;
        }

        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 40px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }

        .btn-secondary:hover {
            background: #667eea;
            color: white;
        }

        .orders-section {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 30px;
        }

        .orders-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .order-list {
            display: grid;
            gap: 15px;
        }

        .order-item {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .order-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .order-id {
            font-family: 'Monaco', monospace;
            font-size: 0.85em;
            color: #666;
        }

        .order-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .status-created { background: #dbeafe; color: #0369a1; }
        .status-processing { background: #fef3c7; color: #b45309; }
        .status-completed { background: #d1fae5; color: #059669; }
        .status-cancelled { background: #fee2e2; color: #dc2626; }

        .order-details {
            color: #666;
            font-size: 0.9em;
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }

        .empty-state svg {
            width: 80px;
            height: 80px;
            margin-bottom: 20px;
            opacity: 0.5;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }
            .stat-value {
                font-size: 1.8em;
            }
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📦 Order Service</h1>
            <p class="subtitle">Pipeline DevOps — FastAPI + Kubernetes + CI/CD</p>
            <div class="status-badge">✓ Sistema Operacional</div>
        </header>

        <div class="grid">
            <div class="card">
                <div class="stat-label">Status da API</div>
                <div class="stat-value">✓</div>
                <div class="stat-label">Operacional</div>
            </div>

            <div class="card">
                <div class="stat-label">Total de Pedidos</div>
                <div class="stat-value" id="total-orders">-</div>
                <div class="stat-label">Carregando...</div>
            </div>

            <div class="card">
                <div class="stat-label">Pedidos Completados</div>
                <div class="stat-value" id="completed-orders">-</div>
                <div class="stat-label">Status Concluído</div>
            </div>

            <div class="card">
                <div class="stat-label">Pedidos Processando</div>
                <div class="stat-value" id="processing-orders">-</div>
                <div class="stat-label">Em andamento</div>
            </div>
        </div>

        <h2 style="color: white; margin-top: 30px; margin-bottom: 20px;">Endpoints Disponíveis</h2>
        <div class="endpoints">
            <div class="endpoint">
                <span class="endpoint-method method-get">GET</span>
                <div class="endpoint-path">/health</div>
                <div class="endpoint-description">Verifica saúde da aplicação</div>
            </div>

            <div class="endpoint">
                <span class="endpoint-method method-get">GET</span>
                <div class="endpoint-path">/metrics</div>
                <div class="endpoint-description">Métricas no formato Prometheus</div>
            </div>

            <div class="endpoint">
                <span class="endpoint-method method-get">GET</span>
                <div class="endpoint-path">/docs</div>
                <div class="endpoint-description">Documentação interativa Swagger UI</div>
            </div>

            <div class="endpoint">
                <span class="endpoint-method method-post">POST</span>
                <div class="endpoint-path">/orders</div>
                <div class="endpoint-description">Criar novo pedido</div>
            </div>

            <div class="endpoint">
                <span class="endpoint-method method-get">GET</span>
                <div class="endpoint-path">/orders</div>
                <div class="endpoint-description">Listar todos os pedidos</div>
            </div>

            <div class="endpoint">
                <span class="endpoint-method method-get">GET</span>
                <div class="endpoint-path">/orders/{id}</div>
                <div class="endpoint-description">Buscar pedido por ID</div>
            </div>

            <div class="endpoint">
                <span class="endpoint-method method-patch">PATCH</span>
                <div class="endpoint-path">/orders/{id}/status</div>
                <div class="endpoint-description">Atualizar status do pedido</div>
            </div>

            <div class="endpoint">
                <span class="endpoint-method method-delete">DELETE</span>
                <div class="endpoint-path">/orders/{id}</div>
                <div class="endpoint-description">Cancelar pedido</div>
            </div>
        </div>

        <div class="action-buttons">
            <a href="/docs" class="btn btn-primary">📖 Swagger UI</a>
            <a href="/metrics" class="btn btn-secondary">📊 Metrics</a>
            <button class="btn btn-secondary" onclick="createSampleOrder()">➕ Criar Pedido Teste</button>
            <button class="btn btn-secondary" onclick="refreshStats()">🔄 Atualizar</button>
        </div>

        <div class="orders-section">
            <h2>Pedidos Recentes</h2>
            <div id="orders-container" class="order-list">
                <div class="loading">Carregando pedidos...</div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;

        async function loadOrders() {
            try {
                const response = await fetch(`${API_BASE}/orders`);
                const orders = await response.json();

                const container = document.getElementById('orders-container');

                if (orders.length === 0) {
                    container.innerHTML = '<div class="empty-state"><p>Nenhum pedido criado ainda</p></div>';
                    return;
                }

                // Reverse para mostrar pedidos mais recentes primeiro
                const reversed = [...orders].reverse();

                container.innerHTML = reversed.map(order => `
                    <div class="order-item">
                        <div class="order-header">
                            <div class="order-id">ID: ${order.id.substring(0, 8)}...</div>
                            <span class="order-status status-${order.status}">${order.status.toUpperCase()}</span>
                        </div>
                        <div class="order-details">
                            <strong>${order.customer}</strong> •
                            ${order.items.length} items •
                            R$ ${order.total.toFixed(2)}
                        </div>
                    </div>
                `).join('');

                updateStats(orders);
            } catch (error) {
                console.error('Erro ao carregar pedidos:', error);
                document.getElementById('orders-container').innerHTML = '<div class="empty-state"><p>Erro ao carregar pedidos</p></div>';
            }
        }

        function updateStats(orders) {
            const total = orders.length;
            const completed = orders.filter(o => o.status === 'completed').length;
            const processing = orders.filter(o => o.status === 'processing').length;

            document.getElementById('total-orders').textContent = total;
            document.getElementById('completed-orders').textContent = completed;
            document.getElementById('processing-orders').textContent = processing;
        }

        async function createSampleOrder() {
            const customers = ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'Carlos Souza'];
            const items = [
                ['Notebook', 'Mouse'],
                ['Teclado', 'Monitor'],
                ['Webcam', 'Fone'],
                ['SSD', 'Cabo USB'],
                ['Mousepad', 'Adaptador HDMI']
            ];

            const randomCustomer = customers[Math.floor(Math.random() * customers.length)];
            const randomItems = items[Math.floor(Math.random() * items.length)];
            const randomTotal = (Math.random() * 5000 + 100).toFixed(2);

            try {
                const response = await fetch(`${API_BASE}/orders`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        customer: randomCustomer,
                        items: randomItems,
                        total: parseFloat(randomTotal)
                    })
                });

                if (response.ok) {
                    await loadOrders();
                    alert('✓ Pedido criado com sucesso!');
                }
            } catch (error) {
                console.error('Erro ao criar pedido:', error);
                alert('✗ Erro ao criar pedido');
            }
        }

        function refreshStats() {
            loadOrders();
        }

        // Carregar pedidos ao iniciar
        loadOrders();

        // Auto-refresh a cada 5 segundos
        setInterval(loadOrders, 5000);
    </script>
</body>
</html>
"""
