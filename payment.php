<?php
require_once 'config.php';

// Prüfen ob Bestellung existiert
$order_id = $_GET['order_id'] ?? null;
if (!$order_id || !isset($_SESSION['pending_order_id']) || $_SESSION['pending_order_id'] != $order_id) {
    header('Location: index.php');
    exit;
}

// Bestellung laden
$stmt = $pdo->prepare("SELECT * FROM orders WHERE id = ? AND customer_id = ?");
$stmt->execute([$order_id, $_SESSION['customer_id']]);
$order = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$order) {
    header('Location: index.php');
    exit;
}

// Stripe Checkout Session erstellen (vereinfacht)
$payment_success = false;

if ($_POST && isset($_POST['simulate_payment'])) {
    // Simuliere erfolgreiche Zahlung
    $stmt = $pdo->prepare("UPDATE orders SET payment_status = 'paid', status = 'processing' WHERE id = ?");
    $stmt->execute([$order_id]);
    
    // Tracking-Nummer generieren (Demo)
    $tracking_number = 'DHL' . str_pad(rand(100000000, 999999999), 12, '0', STR_PAD_LEFT);
    $stmt = $pdo->prepare("UPDATE orders SET tracking_number = ? WHERE id = ?");
    $stmt->execute([$tracking_number, $order_id]);
    
    unset($_SESSION['pending_order_id']);
    $payment_success = true;
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zahlung - ByteDohm.de</title>
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
        </div>
    </nav>

    <div class="container mt-5 pt-4">
        <?php if ($payment_success): ?>
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body text-center">
                            <div class="mb-4">
                                <i class="fas fa-check-circle fa-5x text-success"></i>
                            </div>
                            <h2 class="text-success">Zahlung erfolgreich!</h2>
                            <p class="lead">Vielen Dank für Ihre Bestellung #<?= htmlspecialchars($order['order_number']) ?></p>
                            <p>Sie erhalten in Kürze eine Bestätigungsmail mit allen Details.</p>
                            
                            <div class="row mt-4">
                                <div class="col-md-6">
                                    <div class="card bg-light">
                                        <div class="card-body">
                                            <h6>Bestellnummer</h6>
                                            <p class="fw-bold"><?= htmlspecialchars($order['order_number']) ?></p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="card bg-light">
                                        <div class="card-body">
                                            <h6>Betrag</h6>
                                            <p class="fw-bold"><?= number_format($order['total_amount'], 2) ?>€</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mt-4">
                                <a href="customer/dashboard.php" class="btn btn-primary me-2">
                                    <i class="fas fa-user"></i> Zum Dashboard
                                </a>
                                <a href="index.php" class="btn btn-outline-primary">
                                    <i class="fas fa-home"></i> Zur Startseite
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        <?php else: ?>
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header text-center">
                            <h4><i class="fas fa-credit-card"></i> Zahlung</h4>
                        </div>
                        <div class="card-body">
                            <div class="text-center mb-4">
                                <h5>Bestellung #<?= htmlspecialchars($order['order_number']) ?></h5>
                                <p class="lead text-primary"><?= number_format($order['total_amount'], 2) ?>€</p>
                            </div>
                            
                            <div class="alert alert-info">
                                <h6><i class="fas fa-info-circle"></i> Demo-Modus</h6>
                                <p class="mb-0">Dies ist eine Demo-Umgebung. Die Zahlung wird simuliert.</p>
                            </div>
                            
                            <form method="POST">
                                <div class="card mb-3">
                                    <div class="card-body">
                                        <h6><i class="fas fa-credit-card"></i> Kreditkarte (Demo)</h6>
                                        <div class="row">
                                            <div class="col-12">
                                                <div class="mb-3">
                                                    <input type="text" class="form-control" placeholder="1234 5678 9012 3456" readonly>
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="mb-3">
                                                    <input type="text" class="form-control" placeholder="MM/YY" readonly>
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="mb-3">
                                                    <input type="text" class="form-control" placeholder="123" readonly>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="d-grid gap-2">
                                    <button type="submit" name="simulate_payment" class="btn btn-success btn-lg">
                                        <i class="fas fa-lock"></i> Zahlung abschließen (Demo)
                                    </button>
                                    <a href="checkout.php" class="btn btn-outline-secondary">
                                        <i class="fas fa-arrow-left"></i> Zurück
                                    </a>
                                </div>
                            </form>
                            
                            <div class="text-center mt-3">
                                <small class="text-muted">
                                    <i class="fas fa-lock"></i> Sichere Verschlüsselung
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        <?php endif; ?>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>