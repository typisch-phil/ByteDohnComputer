<?php
require_once 'config.php';

// Warenkorb aus Session laden
$cart = $_SESSION['cart'] ?? [];
$total = 0;

foreach ($cart as $item) {
    $total += $item['price'] * $item['quantity'];
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Warenkorb - ByteDohm.de</title>
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
                    <?php endif; ?>
                    <li class="nav-item">
                        <a class="nav-link active" href="warenkorb.php">
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
                <h1><i class="fas fa-shopping-cart"></i> Warenkorb</h1>
            </div>
        </div>

        <?php if (empty($cart)): ?>
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-info text-center">
                        <h4>Ihr Warenkorb ist leer</h4>
                        <p>Entdecken Sie unsere Produkte und fügen Sie sie zum Warenkorb hinzu.</p>
                        <a href="konfigurator.php" class="btn btn-primary me-2">PC konfigurieren</a>
                        <a href="fertig-pcs.php" class="btn btn-outline-primary">Fertig-PCs ansehen</a>
                    </div>
                </div>
            </div>
        <?php else: ?>
            <div class="row">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5>Artikel im Warenkorb</h5>
                        </div>
                        <div class="card-body">
                            <?php foreach ($cart as $index => $item): ?>
                                <div class="cart-item mb-3 pb-3 border-bottom">
                                    <div class="row align-items-center">
                                        <div class="col-md-6">
                                            <h6><?= htmlspecialchars($item['name']) ?></h6>
                                            <?php if ($item['type'] === 'custom'): ?>
                                                <small class="text-muted">Custom PC Konfiguration</small>
                                                <?php if (isset($item['components'])): ?>
                                                    <div class="mt-2">
                                                        <?php foreach ($item['components'] as $comp): ?>
                                                            <div class="small text-muted">• <?= htmlspecialchars($comp['name']) ?></div>
                                                        <?php endforeach; ?>
                                                    </div>
                                                <?php endif; ?>
                                            <?php else: ?>
                                                <small class="text-muted"><?= htmlspecialchars($item['type']) ?></small>
                                            <?php endif; ?>
                                        </div>
                                        <div class="col-md-2">
                                            <div class="input-group input-group-sm">
                                                <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity(<?= $index ?>, -1)">-</button>
                                                <input type="text" class="form-control text-center" value="<?= $item['quantity'] ?>" readonly>
                                                <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity(<?= $index ?>, 1)">+</button>
                                            </div>
                                        </div>
                                        <div class="col-md-2">
                                            <span class="fw-bold"><?= number_format($item['price'], 2) ?>€</span>
                                        </div>
                                        <div class="col-md-2">
                                            <span class="fw-bold"><?= number_format($item['price'] * $item['quantity'], 2) ?>€</span>
                                        </div>
                                        <div class="col-md-1">
                                            <button class="btn btn-sm btn-outline-danger" onclick="removeItem(<?= $index ?>)">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>Bestellzusammenfassung</h5>
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
                            <hr>
                            <div class="d-flex justify-content-between mb-3">
                                <strong>Gesamtsumme:</strong>
                                <strong><?= number_format($total, 2) ?>€</strong>
                            </div>
                            
                            <?php if (isset($_SESSION['customer_id'])): ?>
                                <div class="d-grid">
                                    <a href="checkout.php" class="btn btn-success">
                                        <i class="fas fa-credit-card"></i> Zur Kasse
                                    </a>
                                </div>
                            <?php else: ?>
                                <div class="alert alert-info">
                                    <small>Bitte melden Sie sich an, um die Bestellung abzuschließen.</small>
                                </div>
                                <div class="d-grid gap-2">
                                    <a href="customer/login.php" class="btn btn-primary">Anmelden</a>
                                    <a href="customer/register.php" class="btn btn-outline-primary">Registrieren</a>
                                </div>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            </div>
        <?php endif; ?>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function updateQuantity(index, change) {
            fetch('warenkorb_update.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'update_quantity',
                    index: index,
                    change: change
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Fehler beim Aktualisieren der Menge');
                }
            });
        }

        function removeItem(index) {
            if (confirm('Artikel aus dem Warenkorb entfernen?')) {
                fetch('warenkorb_update.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'remove_item',
                        index: index
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Fehler beim Entfernen des Artikels');
                    }
                });
            }
        }
    </script>
</body>
</html>