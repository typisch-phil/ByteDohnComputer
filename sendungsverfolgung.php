<?php
require_once 'config.php';

$tracking_number = $_GET['tracking'] ?? '';
$tracking_info = null;
$error = '';

if ($tracking_number) {
    // Tracking-Nummer in der Datenbank suchen
    $stmt = $pdo->prepare("SELECT o.*, c.first_name, c.last_name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.tracking_number = ?");
    $stmt->execute([$tracking_number]);
    $order = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if ($order) {
        $tracking_info = [
            'order_number' => $order['order_number'],
            'customer_name' => $order['first_name'] . ' ' . $order['last_name'],
            'status' => $order['status'],
            'tracking_number' => $order['tracking_number'],
            'created_at' => $order['created_at'],
            'updated_at' => $order['updated_at']
        ];
    } else {
        $error = 'Tracking-Nummer nicht gefunden.';
    }
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sendungsverfolgung - ByteDohm.de</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.php">
                <i class="fas fa-microchip"></i> ByteDohm.de
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="index.php">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="konfigurator.php">PC Konfigurator</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="fertig-pcs.php">Fertig-PCs</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="sendungsverfolgung.php">Sendungsverfolgung</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <?php if(isset($_SESSION['customer_id'])): ?>
                        <li class="nav-item">
                            <a class="nav-link" href="customer/dashboard.php">
                                <i class="fas fa-user"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="customer/logout.php">Abmelden</a>
                        </li>
                    <?php else: ?>
                        <li class="nav-item">
                            <a class="nav-link" href="customer/login.php">Anmelden</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="customer/register.php">Registrieren</a>
                        </li>
                    <?php endif; ?>
                    <li class="nav-item">
                        <a class="nav-link" href="warenkorb.php">
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
                <h1><i class="fas fa-shipping-fast"></i> Sendungsverfolgung</h1>
                <p class="text-muted">Verfolgen Sie den Status Ihrer Bestellung</p>
            </div>
        </div>

        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5>Tracking-Nummer eingeben</h5>
                    </div>
                    <div class="card-body">
                        <form method="GET">
                            <div class="input-group mb-3">
                                <input type="text" 
                                       class="form-control" 
                                       name="tracking" 
                                       placeholder="Tracking-Nummer eingeben..." 
                                       value="<?= htmlspecialchars($tracking_number) ?>"
                                       required>
                                <button class="btn btn-primary" type="submit">
                                    <i class="fas fa-search"></i> Verfolgen
                                </button>
                            </div>
                        </form>
                        
                        <?php if ($error): ?>
                            <div class="alert alert-danger">
                                <?= htmlspecialchars($error) ?>
                            </div>
                        <?php endif; ?>
                        
                        <?php if ($tracking_info): ?>
                            <div class="alert alert-success">
                                <h5>Sendung gefunden!</h5>
                                <div class="row">
                                    <div class="col-md-6">
                                        <p><strong>Bestellnummer:</strong> <?= htmlspecialchars($tracking_info['order_number']) ?></p>
                                        <p><strong>Kunde:</strong> <?= htmlspecialchars($tracking_info['customer_name']) ?></p>
                                        <p><strong>Status:</strong> 
                                            <span class="badge bg-<?= getStatusColor($tracking_info['status']) ?>">
                                                <?= getStatusName($tracking_info['status']) ?>
                                            </span>
                                        </p>
                                    </div>
                                    <div class="col-md-6">
                                        <p><strong>Bestellt am:</strong> <?= date('d.m.Y H:i', strtotime($tracking_info['created_at'])) ?></p>
                                        <p><strong>Letzte Aktualisierung:</strong> <?= date('d.m.Y H:i', strtotime($tracking_info['updated_at'])) ?></p>
                                        <p><strong>Tracking-Nummer:</strong> <?= htmlspecialchars($tracking_info['tracking_number']) ?></p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- DHL Tracking Widget -->
                            <div class="card mt-4">
                                <div class="card-header">
                                    <h6>DHL Sendungsverfolgung</h6>
                                </div>
                                <div class="card-body">
                                    <div class="text-center mb-3">
                                        <p>Für detaillierte Tracking-Informationen besuchen Sie:</p>
                                        <div class="d-grid gap-2 d-md-block">
                                            <a href="https://www.dhl.de/de/privatkunden/pakete-empfangen/verfolgen.html?lang=de&idc=<?= urlencode($tracking_number) ?>" 
                                               target="_blank" 
                                               class="btn btn-warning">
                                                <i class="fas fa-external-link-alt"></i> DHL.de öffnen
                                            </a>
                                            <a href="https://www.17track.net/de/track#nums=<?= urlencode($tracking_number) ?>" 
                                               target="_blank" 
                                               class="btn btn-info">
                                                <i class="fas fa-external-link-alt"></i> 17track.net
                                            </a>
                                            <a href="https://parcelsapp.com/de/tracking/<?= urlencode($tracking_number) ?>" 
                                               target="_blank" 
                                               class="btn btn-success">
                                                <i class="fas fa-external-link-alt"></i> ParcelsApp.com
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
                
                <!-- Hilfe -->
                <div class="card mt-4">
                    <div class="card-header">
                        <h6>Hilfe zur Sendungsverfolgung</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Wo finde ich meine Tracking-Nummer?</h6>
                                <ul class="small">
                                    <li>In der Versandbestätigung per E-Mail</li>
                                    <li>In Ihrem Kundenkonto unter "Bestellungen"</li>
                                    <li>Auf der Rechnung</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Bestellstatus Erklärung:</h6>
                                <ul class="small">
                                    <li><strong>Ausstehend:</strong> Bestellung wird bearbeitet</li>
                                    <li><strong>In Bearbeitung:</strong> PC wird zusammengebaut</li>
                                    <li><strong>Versendet:</strong> Paket ist unterwegs</li>
                                    <li><strong>Zugestellt:</strong> Paket ist angekommen</li>
                                </ul>
                            </div>
                        </div>
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