<?php
require_once 'config.php';

// Komponenten aus der Datenbank laden
$components = [];
$categories = ['cpu', 'motherboard', 'ram', 'gpu', 'ssd', 'case', 'psu', 'cooler'];

foreach($categories as $category) {
    $stmt = $pdo->prepare("SELECT * FROM components WHERE category = ? AND is_active = 1 ORDER BY name");
    $stmt->execute([$category]);
    $components[$category] = $stmt->fetchAll(PDO::FETCH_ASSOC);
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PC Konfigurator - ByteDohm.de</title>
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
                        <a class="nav-link active" href="konfigurator.php">PC Konfigurator</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="fertig-pcs.php">Fertig-PCs</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="sendungsverfolgung.php">Sendungsverfolgung</a>
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
                <h1 class="display-4 text-center mb-5">PC Konfigurator</h1>
            </div>
        </div>

        <div class="row">
            <!-- Komponenten Auswahl -->
            <div class="col-lg-8">
                <div class="configurator-steps">
                    <!-- CPU Sektion -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5><i class="fas fa-microchip"></i> Prozessor (CPU)</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <?php foreach($components['cpu'] as $cpu): ?>
                                    <div class="col-md-6 mb-3">
                                        <div class="component-card" data-component="cpu" data-id="<?= $cpu['id'] ?>" data-price="<?= $cpu['price'] ?>">
                                            <div class="card h-100">
                                                <div class="card-body">
                                                    <h6 class="card-title"><?= htmlspecialchars($cpu['name']) ?></h6>
                                                    <p class="text-muted small"><?= htmlspecialchars(json_decode($cpu['specifications'], true)['cores'] ?? '') ?> Kerne</p>
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <span class="price fw-bold"><?= number_format($cpu['price'], 2) ?>€</span>
                                                        <button class="btn btn-outline-primary btn-sm select-component">Auswählen</button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </div>

                    <!-- Mainboard Sektion -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5><i class="fas fa-memory"></i> Mainboard</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <?php foreach($components['motherboard'] as $mb): ?>
                                    <div class="col-md-6 mb-3">
                                        <div class="component-card" data-component="motherboard" data-id="<?= $mb['id'] ?>" data-price="<?= $mb['price'] ?>">
                                            <div class="card h-100">
                                                <div class="card-body">
                                                    <h6 class="card-title"><?= htmlspecialchars($mb['name']) ?></h6>
                                                    <p class="text-muted small"><?= htmlspecialchars(json_decode($mb['specifications'], true)['socket'] ?? '') ?></p>
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <span class="price fw-bold"><?= number_format($mb['price'], 2) ?>€</span>
                                                        <button class="btn btn-outline-primary btn-sm select-component">Auswählen</button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </div>

                    <!-- RAM Sektion -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5><i class="fas fa-memory"></i> Arbeitsspeicher (RAM)</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <?php foreach($components['ram'] as $ram): ?>
                                    <div class="col-md-6 mb-3">
                                        <div class="component-card" data-component="ram" data-id="<?= $ram['id'] ?>" data-price="<?= $ram['price'] ?>">
                                            <div class="card h-100">
                                                <div class="card-body">
                                                    <h6 class="card-title"><?= htmlspecialchars($ram['name']) ?></h6>
                                                    <p class="text-muted small"><?= htmlspecialchars(json_decode($ram['specifications'], true)['capacity'] ?? '') ?></p>
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <span class="price fw-bold"><?= number_format($ram['price'], 2) ?>€</span>
                                                        <button class="btn btn-outline-primary btn-sm select-component">Auswählen</button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </div>

                    <!-- GPU Sektion -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5><i class="fas fa-tv"></i> Grafikkarte (GPU)</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <?php foreach($components['gpu'] as $gpu): ?>
                                    <div class="col-md-6 mb-3">
                                        <div class="component-card" data-component="gpu" data-id="<?= $gpu['id'] ?>" data-price="<?= $gpu['price'] ?>">
                                            <div class="card h-100">
                                                <div class="card-body">
                                                    <h6 class="card-title"><?= htmlspecialchars($gpu['name']) ?></h6>
                                                    <p class="text-muted small"><?= htmlspecialchars(json_decode($gpu['specifications'], true)['memory'] ?? '') ?></p>
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <span class="price fw-bold"><?= number_format($gpu['price'], 2) ?>€</span>
                                                        <button class="btn btn-outline-primary btn-sm select-component">Auswählen</button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </div>

                    <!-- Weitere Komponenten... -->
                </div>
            </div>

            <!-- Zusammenfassung -->
            <div class="col-lg-4">
                <div class="card sticky-top">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> Ihre Konfiguration</h5>
                    </div>
                    <div class="card-body">
                        <div id="configuration-summary">
                            <p class="text-muted">Wählen Sie Komponenten aus, um Ihre Konfiguration zu erstellen.</p>
                        </div>
                        <hr>
                        <div class="d-flex justify-content-between">
                            <strong>Gesamtpreis:</strong>
                            <strong id="total-price">0,00€</strong>
                        </div>
                        <div class="d-grid gap-2 mt-3">
                            <button class="btn btn-success" id="add-to-cart" disabled>
                                <i class="fas fa-shopping-cart"></i> In den Warenkorb
                            </button>
                            <button class="btn btn-outline-primary" id="save-configuration" disabled>
                                <i class="fas fa-save"></i> Konfiguration speichern
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // PHP Daten für JavaScript verfügbar machen
        const components = <?= json_encode($components) ?>;
        
        // Konfigurator JavaScript
        class PCConfigurator {
            constructor() {
                this.selectedComponents = {};
                this.totalPrice = 0;
                this.initEventListeners();
            }

            initEventListeners() {
                document.querySelectorAll('.select-component').forEach(button => {
                    button.addEventListener('click', (e) => {
                        const card = e.target.closest('.component-card');
                        const component = card.dataset.component;
                        const id = card.dataset.id;
                        const price = parseFloat(card.dataset.price);
                        
                        this.selectComponent(component, id, price);
                    });
                });

                document.getElementById('add-to-cart').addEventListener('click', () => {
                    this.addToCart();
                });

                document.getElementById('save-configuration').addEventListener('click', () => {
                    this.saveConfiguration();
                });
            }

            selectComponent(category, id, price) {
                // Vorherige Auswahl entfernen
                document.querySelectorAll(`[data-component="${category}"] .select-component`).forEach(btn => {
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-primary');
                    btn.textContent = 'Auswählen';
                });

                // Neue Auswahl markieren
                const selectedCard = document.querySelector(`[data-component="${category}"][data-id="${id}"]`);
                const button = selectedCard.querySelector('.select-component');
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-success');
                button.textContent = 'Ausgewählt';

                // Komponente speichern
                this.selectedComponents[category] = {
                    id: id,
                    price: price,
                    name: selectedCard.querySelector('.card-title').textContent
                };

                this.updateSummary();
            }

            updateSummary() {
                const summaryDiv = document.getElementById('configuration-summary');
                let html = '';
                this.totalPrice = 0;

                for (const [category, component] of Object.entries(this.selectedComponents)) {
                    html += `<div class="d-flex justify-content-between mb-2">
                        <span>${component.name}</span>
                        <span>${component.price.toFixed(2)}€</span>
                    </div>`;
                    this.totalPrice += component.price;
                }

                summaryDiv.innerHTML = html || '<p class="text-muted">Wählen Sie Komponenten aus.</p>';
                document.getElementById('total-price').textContent = this.totalPrice.toFixed(2) + '€';
                
                // Buttons aktivieren wenn Komponenten ausgewählt
                const hasComponents = Object.keys(this.selectedComponents).length > 0;
                document.getElementById('add-to-cart').disabled = !hasComponents;
                document.getElementById('save-configuration').disabled = !hasComponents;
            }

            addToCart() {
                fetch('warenkorb_add.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        type: 'custom',
                        components: this.selectedComponents,
                        total_price: this.totalPrice
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Konfiguration wurde zum Warenkorb hinzugefügt!');
                        window.location.href = 'warenkorb.php';
                    } else {
                        alert('Fehler beim Hinzufügen zum Warenkorb: ' + data.message);
                    }
                });
            }

            saveConfiguration() {
                const name = prompt('Name für die Konfiguration:');
                if (!name) return;

                fetch('save_configuration.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: name,
                        components: this.selectedComponents,
                        total_price: this.totalPrice
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Konfiguration wurde gespeichert!');
                    } else {
                        alert('Fehler beim Speichern: ' + data.message);
                    }
                });
            }
        }

        // Konfigurator initialisieren
        const configurator = new PCConfigurator();
    </script>
</body>
</html>