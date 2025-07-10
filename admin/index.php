<?php
require_once '../config.php';

// Prüfen ob Admin angemeldet
if (!isset($_SESSION['admin_id'])) {
    header('Location: login.php');
    exit;
}

// Dashboard Statistiken
$stats = [];

// Bestellungen heute
$stmt = $pdo->prepare("SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as revenue FROM orders WHERE DATE(created_at) = CURDATE()");
$stmt->execute();
$today = $stmt->fetch(PDO::FETCH_ASSOC);
$stats['today_orders'] = $today['count'];
$stats['today_revenue'] = $today['revenue'];

// Bestellungen total
$stmt = $pdo->prepare("SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as revenue FROM orders");
$stmt->execute();
$total = $stmt->fetch(PDO::FETCH_ASSOC);
$stats['total_orders'] = $total['count'];
$stats['total_revenue'] = $total['revenue'];

// Kunden total
$stmt = $pdo->prepare("SELECT COUNT(*) as count FROM customers");
$stmt->execute();
$stats['total_customers'] = $stmt->fetchColumn();

// Komponenten total
$stmt = $pdo->prepare("SELECT COUNT(*) as count FROM components WHERE is_active = 1");
$stmt->execute();
$stats['total_components'] = $stmt->fetchColumn();

// Letzte Bestellungen
$stmt = $pdo->prepare("SELECT o.*, c.first_name, c.last_name FROM orders o JOIN customers c ON o.customer_id = c.id ORDER BY o.created_at DESC LIMIT 10");
$stmt->execute();
$recent_orders = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - ByteDohm.de</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="index.php">
                <i class="fas fa-cogs"></i> ByteDohm Admin
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="index.php">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="orders.php">Bestellungen</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="customers.php">Kunden</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="components.php">Komponenten</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="prebuilts.php">Fertig-PCs</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="newsletter.php">Newsletter</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="../index.php" target="_blank">
                            <i class="fas fa-external-link-alt"></i> Website
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="logout.php">
                            <i class="fas fa-sign-out-alt"></i> Abmelden
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <h1>Dashboard</h1>
                <p class="text-muted">Willkommen im ByteDohm Admin-Panel</p>
            </div>
        </div>

        <!-- Statistiken -->
        <div class="row mb-4">
            <div class="col-xl-3 col-md-6">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <div class="text-white-50 small">Heute</div>
                                <div class="text-lg fw-bold"><?= $stats['today_orders'] ?> Bestellungen</div>
                                <div class="text-white-75"><?= number_format($stats['today_revenue'], 2) ?>€</div>
                            </div>
                            <div class="fa-3x text-white-25">
                                <i class="fas fa-shopping-bag"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-xl-3 col-md-6">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <div class="text-white-50 small">Gesamt</div>
                                <div class="text-lg fw-bold"><?= $stats['total_orders'] ?> Bestellungen</div>
                                <div class="text-white-75"><?= number_format($stats['total_revenue'], 2) ?>€</div>
                            </div>
                            <div class="fa-3x text-white-25">
                                <i class="fas fa-euro-sign"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-xl-3 col-md-6">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <div class="text-white-50 small">Kunden</div>
                                <div class="text-lg fw-bold"><?= $stats['total_customers'] ?></div>
                                <div class="text-white-75">Registrierte Nutzer</div>
                            </div>
                            <div class="fa-3x text-white-25">
                                <i class="fas fa-users"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-xl-3 col-md-6">
                <div class="card bg-warning text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <div class="text-white-50 small">Komponenten</div>
                                <div class="text-lg fw-bold"><?= $stats['total_components'] ?></div>
                                <div class="text-white-75">Aktive Artikel</div>
                            </div>
                            <div class="fa-3x text-white-25">
                                <i class="fas fa-microchip"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Letzte Bestellungen -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5>Letzte Bestellungen</h5>
                        <a href="orders.php" class="btn btn-primary btn-sm">Alle Bestellungen</a>
                    </div>
                    <div class="card-body">
                        <?php if (empty($recent_orders)): ?>
                            <p class="text-muted">Noch keine Bestellungen vorhanden.</p>
                        <?php else: ?>
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Bestellnummer</th>
                                            <th>Kunde</th>
                                            <th>Betrag</th>
                                            <th>Status</th>
                                            <th>Datum</th>
                                            <th>Aktionen</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach ($recent_orders as $order): ?>
                                            <tr>
                                                <td>#<?= htmlspecialchars($order['order_number']) ?></td>
                                                <td><?= htmlspecialchars($order['first_name'] . ' ' . $order['last_name']) ?></td>
                                                <td><?= number_format($order['total_amount'], 2) ?>€</td>
                                                <td>
                                                    <span class="badge bg-<?= getStatusColor($order['status']) ?>">
                                                        <?= getStatusName($order['status']) ?>
                                                    </span>
                                                </td>
                                                <td><?= date('d.m.Y H:i', strtotime($order['created_at'])) ?></td>
                                                <td>
                                                    <a href="order_detail.php?id=<?= $order['id'] ?>" class="btn btn-sm btn-outline-primary">
                                                        <i class="fas fa-eye"></i>
                                                    </a>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    </tbody>
                                </table>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>

<?php
function getStatusColor($status) {
    switch ($status) {
        case 'pending': return 'warning';
        case 'processing': return 'info';
        case 'shipped': return 'primary';
        case 'delivered': return 'success';
        case 'cancelled': return 'danger';
        default: return 'secondary';
    }
}

function getStatusName($status) {
    switch ($status) {
        case 'pending': return 'Ausstehend';
        case 'processing': return 'In Bearbeitung';
        case 'shipped': return 'Versendet';
        case 'delivered': return 'Zugestellt';
        case 'cancelled': return 'Storniert';
        default: return 'Unbekannt';
    }
}
?>