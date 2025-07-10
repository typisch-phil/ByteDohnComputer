<?php
require_once 'config.php';

// Prüfen ob angemeldet
if (!isset($_SESSION['customer_id'])) {
    header('Location: customer/login.php');
    exit;
}

// Warenkorb prüfen
$cart = $_SESSION['cart'] ?? [];
if (empty($cart)) {
    header('Location: warenkorb.php');
    exit;
}

$customer_id = $_SESSION['customer_id'];

// Kundendaten laden
$stmt = $pdo->prepare("SELECT * FROM customers WHERE id = ?");
$stmt->execute([$customer_id]);
$customer = $stmt->fetch(PDO::FETCH_ASSOC);

// Warenkorb-Gesamtpreis berechnen
$total = 0;
foreach ($cart as $item) {
    $total += $item['price'] * $item['quantity'];
}

$error = '';
$success = '';

if ($_POST && isset($_POST['place_order'])) {
    try {
        // Bestellnummer generieren
        $order_number = 'BD-' . date('Y') . '-' . str_pad(rand(1, 99999), 5, '0', STR_PAD_LEFT);
        
        // Bestellung erstellen
        $stmt = $pdo->prepare("INSERT INTO orders (customer_id, order_number, order_type, total_amount, status, payment_status, created_at) VALUES (?, ?, ?, ?, 'pending', 'pending', NOW())");
        $stmt->execute([$customer_id, $order_number, 'mixed', $total]);
        $order_id = $pdo->lastInsertId();
        
        // Bestellpositionen erstellen
        foreach ($cart as $item) {
            if ($item['type'] === 'custom') {
                // Custom PC
                $stmt = $pdo->prepare("INSERT INTO order_items (order_id, item_type, item_id, item_name, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)");
                $stmt->execute([$order_id, 'custom', 0, $item['name'], $item['quantity'], $item['price'], $item['price'] * $item['quantity']]);
            } else {
                // Prebuilt PC
                $stmt = $pdo->prepare("INSERT INTO order_items (order_id, item_type, item_id, item_name, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)");
                $stmt->execute([$order_id, 'prebuilt', $item['id'], $item['name'], $item['quantity'], $item['price'], $item['price'] * $item['quantity']]);
            }
        }
        
        // Rechnung erstellen
        $invoice_number = 'RE-' . date('Y') . '-' . str_pad($order_id, 6, '0', STR_PAD_LEFT);
        $stmt = $pdo->prepare("INSERT INTO invoices (order_id, invoice_number, issue_date, total_amount, tax_amount, status) VALUES (?, ?, NOW(), ?, 0.0, 'draft')");
        $stmt->execute([$order_id, $invoice_number, $total]);
        
        // Warenkorb leeren
        $_SESSION['cart'] = [];
        
        // Zur Stripe-Zahlung weiterleiten (vereinfacht)
        $_SESSION['pending_order_id'] = $order_id;
        header('Location: payment.php?order_id=' . $order_id);
        exit;
        
    } catch (Exception $e) {
        $error = 'Fehler beim Erstellen der Bestellung: ' . $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kasse - ByteDohm.de</title>
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
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="warenkorb.php">
                    <i class="fas fa-arrow-left"></i> Zurück zum Warenkorb
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-5 pt-4">
        <div class="row">
            <div class="col-12">
                <h1><i class="fas fa-credit-card"></i> Kasse</h1>
                <p class="text-muted">Bestellung abschließen</p>
            </div>
        </div>

        <?php if ($error): ?>
            <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>

        <div class="row">
            <!-- Bestellübersicht -->
            <div class="col-lg-8">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Bestellübersicht</h5>
                    </div>
                    <div class="card-body">
                        <?php foreach ($cart as $item): ?>
                            <div class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom">
                                <div>
                                    <h6><?= htmlspecialchars($item['name']) ?></h6>
                                    <?php if ($item['type'] === 'custom' && isset($item['components'])): ?>
                                        <div class="small text-muted">
                                            <?php foreach ($item['components'] as $comp): ?>
                                                <div>• <?= htmlspecialchars($comp['name']) ?></div>
                                            <?php endforeach; ?>
                                        </div>
                                    <?php endif; ?>
                                    <small class="text-muted">Menge: <?= $item['quantity'] ?></small>
                                </div>
                                <div class="text-end">
                                    <div class="fw-bold"><?= number_format($item['price'] * $item['quantity'], 2) ?>€</div>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>

                <!-- Kundendaten -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Ihre Daten</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Name:</strong> <?= htmlspecialchars($customer['first_name'] . ' ' . $customer['last_name']) ?></p>
                                <p><strong>E-Mail:</strong> <?= htmlspecialchars($customer['email']) ?></p>
                            </div>
                            <div class="col-md-6">
                                <?php if ($customer['address']): ?>
                                    <p><strong>Adresse:</strong><br>
                                    <?= nl2br(htmlspecialchars($customer['address'])) ?></p>
                                <?php else: ?>
                                    <div class="alert alert-warning">
                                        <small>Keine Lieferadresse hinterlegt. Bitte ergänzen Sie Ihre Adresse in Ihrem Profil.</small>
                                        <a href="customer/profile.php" class="btn btn-sm btn-outline-warning mt-2">Profil bearbeiten</a>
                                    </div>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bestellsumme -->
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Bestellsumme</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-between mb-2">
                            <span>Zwischensumme:</span>
                            <span><?= number_format($total, 2) ?>€</span>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span>Versand:</span>
                            <span>Kostenlos</span>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span>MwSt.:</span>
                            <span>Nicht ausgewiesen*</span>
                        </div>
                        <hr>
                        <div class="d-flex justify-content-between mb-3">
                            <strong>Gesamtsumme:</strong>
                            <strong><?= number_format($total, 2) ?>€</strong>
                        </div>
                        
                        <form method="POST">
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="terms" required>
                                    <label class="form-check-label" for="terms">
                                        Ich akzeptiere die <a href="agb.php" target="_blank">AGB</a> und <a href="datenschutz.php" target="_blank">Datenschutzerklärung</a>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="d-grid">
                                <button type="submit" name="place_order" class="btn btn-success btn-lg">
                                    <i class="fas fa-lock"></i> Jetzt bestellen
                                </button>
                            </div>
                        </form>
                        
                        <div class="text-center mt-3">
                            <small class="text-muted">
                                *Kleinunternehmer gemäß §19 UStG<br>
                                Sichere Zahlung mit Stripe
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>