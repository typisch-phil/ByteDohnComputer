<?php
// ByteDohm.de - PHP Version
// Database Configuration
$host = '45.88.108.231';
$dbname = 'u6560-6636_bytedohm';
$username = 'u6560-6636_bytedohm';
$password = 'HeikoCindy-8';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    die("Verbindungsfehler: " . $e->getMessage());
}

// Session starten
session_start();
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ByteDohm.de - Ihr PC-Konfigurator</title>
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

    <!-- Hero Section -->
    <div class="hero-section">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6">
                    <h1 class="display-4 fw-bold text-white mb-4">
                        Ihr <span class="text-primary">Traum-PC</span><br>
                        nach Maß konfiguriert
                    </h1>
                    <p class="lead text-white-50 mb-4">
                        Erstellen Sie Ihren perfekten Gaming-, Workstation- oder Office-PC mit unserem intuitiven Konfigurator. 
                        Professionelle Beratung und Premium-Komponenten inklusive.
                    </p>
                    <div class="d-flex gap-3">
                        <a href="konfigurator.php" class="btn btn-primary btn-lg">
                            <i class="fas fa-cogs"></i> Jetzt konfigurieren
                        </a>
                        <a href="fertig-pcs.php" class="btn btn-outline-light btn-lg">
                            <i class="fas fa-desktop"></i> Fertig-PCs ansehen
                        </a>
                    </div>
                </div>
                <div class="col-lg-6 text-center">
                    <div class="hero-image">
                        <i class="fas fa-desktop fa-10x text-primary"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Features Section -->
    <div class="container my-5 py-5">
        <div class="row text-center mb-5">
            <div class="col-12">
                <h2 class="display-5 fw-bold mb-3">Warum ByteDohm?</h2>
                <p class="lead text-muted">Ihre Vorteile auf einen Blick</p>
            </div>
        </div>
        
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center p-4">
                        <div class="feature-icon mb-3">
                            <i class="fas fa-cogs fa-3x text-primary"></i>
                        </div>
                        <h5 class="card-title">Intelligenter Konfigurator</h5>
                        <p class="card-text text-muted">
                            Unser Konfigurator prüft automatisch die Kompatibilität aller Komponenten und 
                            schlägt optimale Kombinationen vor.
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center p-4">
                        <div class="feature-icon mb-3">
                            <i class="fas fa-shipping-fast fa-3x text-primary"></i>
                        </div>
                        <h5 class="card-title">Schneller Versand</h5>
                        <p class="card-text text-muted">
                            Professionelle Montage und schneller, sicherer Versand mit DHL. 
                            Tracking-Informationen inklusive.
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center p-4">
                        <div class="feature-icon mb-3">
                            <i class="fas fa-headset fa-3x text-primary"></i>
                        </div>
                        <h5 class="card-title">Persönlicher Support</h5>
                        <p class="card-text text-muted">
                            Unser Expertenteam steht Ihnen vor und nach dem Kauf mit Rat und Tat zur Seite.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5><i class="fas fa-microchip"></i> ByteDohm.de</h5>
                    <p class="text-muted">Ihr Experte für maßgeschneiderte PC-Systeme</p>
                </div>
                <div class="col-md-6">
                    <h6>Rechtliches</h6>
                    <ul class="list-unstyled">
                        <li><a href="agb.php" class="text-muted">AGB</a></li>
                        <li><a href="datenschutz.php" class="text-muted">Datenschutz</a></li>
                        <li><a href="widerruf.php" class="text-muted">Widerrufsrecht</a></li>
                        <li><a href="zahlungsmethoden.php" class="text-muted">Zahlungsmethoden</a></li>
                        <li><a href="newsletter/abmelden.php" class="text-muted">Newsletter abmelden</a></li>
                    </ul>
                </div>
            </div>
            <hr class="my-3">
            <div class="row">
                <div class="col-12 text-center">
                    <p class="mb-0 text-muted">&copy; 2025 ByteDohm.de - Alle Rechte vorbehalten</p>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>