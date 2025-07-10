<?php
require_once '../config.php';

// Prüfen ob angemeldet
if (!isset($_SESSION['customer_id'])) {
    header('Location: login.php');
    exit;
}

$customer_id = $_SESSION['customer_id'];

// Kundendaten laden
$stmt = $pdo->prepare("SELECT * FROM customers WHERE id = ?");
$stmt->execute([$customer_id]);
$customer = $stmt->fetch(PDO::FETCH_ASSOC);

// Bestellungen laden
$stmt = $pdo->prepare("SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC LIMIT 5");
$stmt->execute([$customer_id]);
$orders = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Konfigurationen laden
$stmt = $pdo->prepare("SELECT * FROM configurations WHERE customer_id = ? ORDER BY created_at DESC LIMIT 5");
$stmt->execute([$customer_id]);
$configurations = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Statistiken
$stmt = $pdo->prepare("SELECT COUNT(*) as order_count, COALESCE(SUM(total_amount), 0) as total_spent FROM orders WHERE customer_id = ?");
$stmt->execute([$customer_id]);
$stats = $stmt->fetch(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - ByteDohm.de</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="../index.php">
                <i class="fas fa-microchip"></i> ByteDohm.de
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="../index.php">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="../konfigurator.php">PC Konfigurator</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="../fertig-pcs.php">Fertig-PCs</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link active" href="dashboard.php">
                            <i class="fas fa-user"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="logout.php">Abmelden</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="../warenkorb.php">
                            <i class="fas fa-shopping-cart"></i> Warenkorb
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5 pt-4">
        <div class="row">
            <div class="col-12">
                <h1>Willkommen, <?= htmlspecialchars($customer['first_name']) ?>!</h1>
                <p class="text-muted">Verwalten Sie Ihre Bestellungen und Konfigurationen</p>
            </div>
        </div>

        <!-- Statistiken -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body text-center">
                        <i class="fas fa-shopping-bag fa-2x text-primary mb-2"></i>
                        <h4><?= $stats['order_count'] ?></h4>
                        <p class="text-muted">Bestellungen</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body text-center">
                        <i class="fas fa-euro-sign fa-2x text-success mb-2"></i>
                        <h4><?= number_format($stats['total_spent'], 2) ?>€</h4>
                        <p class="text-muted">Ausgegeben</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body text-center">
                        <i class="fas fa-cogs fa-2x text-info mb-2"></i>
                        <h4><?= count($configurations) ?></h4>
                        <p class="text-muted">Konfigurationen</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Bestellungen -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-shopping-bag"></i> Letzte Bestellungen</h5>
                        <a href="orders.php" class="btn btn-sm btn-outline-primary">Alle anzeigen</a>
                    </div>
                    <div class="card-body">
                        <?php if (empty($orders)): ?>
                            <p class="text-muted">Noch keine Bestellungen vorhanden.</p>
                            <a href="../konfigurator.php" class="btn btn-primary">PC konfigurieren</a>
                        <?php else: ?>
                            <?php foreach ($orders as $order): ?>
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <div>
                                        <h6 class="mb-1">Bestellung #<?= htmlspecialchars($order['order_number']) ?></h6>
                                        <small class="text-muted"><?= date('d.m.Y', strtotime($order['created_at'])) ?></small>
                                    </div>
                                    <div class="text-end">
                                        <div class="fw-bold"><?= number_format($order['total_amount'], 2) ?>€</div>
                                        <span class="badge bg-<?= getStatusColor($order['status']) ?>">
                                            <?= getStatusName($order['status']) ?>
                                        </span>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </div>
                </div>
            </div>

            <!-- Konfigurationen -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-cogs"></i> Gespeicherte Konfigurationen</h5>
                        <a href="configurations.php" class="btn btn-sm btn-outline-primary">Alle anzeigen</a>
                    </div>
                    <div class="card-body">
                        <?php if (empty($configurations)): ?>
                            <p class="text-muted">Noch keine Konfigurationen gespeichert.</p>
                            <a href="../konfigurator.php" class="btn btn-primary">PC konfigurieren</a>
                        <?php else: ?>
                            <?php foreach ($configurations as $config): ?>
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <div>
                                        <h6 class="mb-1"><?= htmlspecialchars($config['name']) ?></h6>
                                        <small class="text-muted"><?= date('d.m.Y', strtotime($config['created_at'])) ?></small>
                                    </div>
                                    <div class="text-end">
                                        <div class="fw-bold"><?= number_format($config['total_price'], 2) ?>€</div>
                                        <div class="btn-group btn-group-sm">
                                            <a href="configuration_detail.php?id=<?= $config['id'] ?>" class="btn btn-outline-primary">
                                                <i class="fas fa-eye"></i>
                                            </a>
                                            <a href="../konfigurator.php?load=<?= $config['id'] ?>" class="btn btn-outline-secondary">
                                                <i class="fas fa-edit"></i>
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>

        <!-- Profil -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-user"></i> Profil</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Name:</strong> <?= htmlspecialchars($customer['first_name'] . ' ' . $customer['last_name']) ?></p>
                                <p><strong>E-Mail:</strong> <?= htmlspecialchars($customer['email']) ?></p>
                                <p><strong>Newsletter:</strong> <?= $customer['newsletter_subscription'] ? 'Abonniert' : 'Nicht abonniert' ?></p>
                            </div>
                            <div class="col-md-6">
                                <?php if ($customer['address']): ?>
                                    <p><strong>Adresse:</strong><br>
                                    <?= nl2br(htmlspecialchars($customer['address'])) ?></p>
                                <?php else: ?>
                                    <p class="text-muted">Keine Adresse hinterlegt</p>
                                <?php endif; ?>
                                <p><strong>Mitglied seit:</strong> <?= date('d.m.Y', strtotime($customer['created_at'])) ?></p>
                            </div>
                        </div>
                        <a href="profile.php" class="btn btn-outline-primary">Profil bearbeiten</a>
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