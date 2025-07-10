<?php
require_once 'config.php';

// Prebuilt PCs aus der Datenbank laden
$stmt = $pdo->prepare("SELECT * FROM prebuilt_pcs WHERE is_active = 1 ORDER BY category, price");
$stmt->execute();
$prebuilt_pcs = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Nach Kategorien gruppieren
$categories = [];
foreach ($prebuilt_pcs as $pc) {
    $categories[$pc['category']][] = $pc;
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fertig-PCs - ByteDohm.de</title>
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
                        <a class="nav-link active" href="fertig-pcs.php">Fertig-PCs</a>
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
                <h1 class="display-4 text-center mb-5">Fertig-PCs</h1>
                <p class="lead text-center text-muted mb-5">
                    Professionell zusammengestellte PC-Systeme für jeden Anwendungsbereich
                </p>
            </div>
        </div>

        <!-- Filter Buttons -->
        <div class="row mb-4">
            <div class="col-12 text-center">
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-outline-primary active" data-filter="all">Alle</button>
                    <?php foreach (array_keys($categories) as $category): ?>
                        <button type="button" class="btn btn-outline-primary" data-filter="<?= $category ?>">
                            <?= getCategoryName($category) ?>
                        </button>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>

        <!-- PC Karten -->
        <div class="row">
            <?php foreach ($prebuilt_pcs as $pc): 
                $specifications = json_decode($pc['specifications'], true);
                $features = json_decode($pc['features'], true);
            ?>
                <div class="col-lg-4 col-md-6 mb-4 pc-card" data-category="<?= $pc['category'] ?>">
                    <div class="card h-100 shadow-sm">
                        <?php if ($pc['image_url']): ?>
                            <img src="<?= htmlspecialchars($pc['image_url']) ?>" class="card-img-top" alt="<?= htmlspecialchars($pc['name']) ?>" style="height: 200px; object-fit: cover;">
                        <?php else: ?>
                            <div class="card-img-top d-flex align-items-center justify-content-center bg-light" style="height: 200px;">
                                <i class="fas fa-desktop fa-4x text-muted"></i>
                            </div>
                        <?php endif; ?>
                        
                        <div class="card-body d-flex flex-column">
                            <div class="mb-auto">
                                <h5 class="card-title"><?= htmlspecialchars($pc['name']) ?></h5>
                                <p class="card-text text-muted"><?= htmlspecialchars($pc['description']) ?></p>
                                
                                <!-- Spezifikationen -->
                                <div class="mb-3">
                                    <h6 class="text-primary">Spezifikationen:</h6>
                                    <ul class="list-unstyled small">
                                        <?php foreach ($specifications as $key => $value): ?>
                                            <li><strong><?= htmlspecialchars($key) ?>:</strong> <?= htmlspecialchars($value) ?></li>
                                        <?php endforeach; ?>
                                    </ul>
                                </div>

                                <!-- Features -->
                                <?php if (!empty($features)): ?>
                                    <div class="mb-3">
                                        <h6 class="text-primary">Features:</h6>
                                        <ul class="list-unstyled small">
                                            <?php foreach ($features as $feature): ?>
                                                <li><i class="fas fa-check text-success"></i> <?= htmlspecialchars($feature) ?></li>
                                            <?php endforeach; ?>
                                        </ul>
                                    </div>
                                <?php endif; ?>
                            </div>
                            
                            <div class="mt-auto">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="h4 text-primary mb-0"><?= number_format($pc['price'], 2) ?>€</span>
                                    <span class="badge bg-secondary"><?= getCategoryName($pc['category']) ?></span>
                                </div>
                                <div class="d-grid gap-2 mt-3">
                                    <button class="btn btn-primary" onclick="addToCart('prebuilt', <?= $pc['id'] ?>, '<?= htmlspecialchars($pc['name']) ?>', <?= $pc['price'] ?>)">
                                        <i class="fas fa-shopping-cart"></i> In den Warenkorb
                                    </button>
                                    <a href="pc_detail.php?id=<?= $pc['id'] ?>" class="btn btn-outline-secondary">
                                        <i class="fas fa-info-circle"></i> Details ansehen
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>

        <?php if (empty($prebuilt_pcs)): ?>
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-info text-center">
                        <h4>Keine Fertig-PCs verfügbar</h4>
                        <p>Derzeit sind keine vorkonfigurierten PCs verfügbar. Nutzen Sie unseren Konfigurator, um Ihren individuellen PC zusammenzustellen.</p>
                        <a href="konfigurator.php" class="btn btn-primary">PC konfigurieren</a>
                    </div>
                </div>
            </div>
        <?php endif; ?>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Filter Funktionalität
        document.querySelectorAll('[data-filter]').forEach(button => {
            button.addEventListener('click', function() {
                const filter = this.dataset.filter;
                
                // Button Status aktualisieren
                document.querySelectorAll('[data-filter]').forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // PC Karten filtern
                document.querySelectorAll('.pc-card').forEach(card => {
                    if (filter === 'all' || card.dataset.category === filter) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });

        function addToCart(type, id, name, price) {
            fetch('warenkorb_add.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: type,
                    id: id,
                    name: name,
                    price: price,
                    quantity: 1
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('PC wurde zum Warenkorb hinzugefügt!');
                } else {
                    alert('Fehler beim Hinzufügen zum Warenkorb: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ein Fehler ist aufgetreten.');
            });
        }
    </script>
</body>
</html>

<?php
function getCategoryName($category) {
    switch ($category) {
        case 'gaming': return 'Gaming';
        case 'workstation': return 'Workstation';
        case 'office': return 'Office';
        case 'server': return 'Server';
        case 'budget': return 'Budget';
        case 'premium': return 'Premium';
        default: return ucfirst($category);
    }
}
?>