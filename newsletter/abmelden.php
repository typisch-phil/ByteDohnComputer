<?php
require_once '../config.php';

$success = false;
$error = '';

if ($_POST) {
    $email = $_POST['email'] ?? '';
    
    if (!$email) {
        $error = 'Bitte geben Sie eine E-Mail-Adresse ein.';
    } else {
        try {
            // Kunde in der Datenbank finden
            $stmt = $pdo->prepare("SELECT id FROM customers WHERE email = ?");
            $stmt->execute([$email]);
            $customer = $stmt->fetch(PDO::FETCH_ASSOC);
            
            if ($customer) {
                // Newsletter-Abonnement deaktivieren
                $stmt = $pdo->prepare("UPDATE customers SET newsletter_subscription = 0 WHERE id = ?");
                $stmt->execute([$customer['id']]);
            }
            
            // Auch wenn kein Kunde gefunden wird, positive Nachricht zeigen (Datenschutz)
            $success = true;
            
        } catch (Exception $e) {
            $error = 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newsletter abmelden - ByteDohm.de</title>
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
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="../index.php">Zurück zur Startseite</a>
            </div>
        </div>
    </nav>

    <div class="container mt-5 pt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h4 class="mb-0">
                            <i class="fas fa-envelope-open"></i> 
                            Newsletter abmelden
                        </h4>
                    </div>
                    <div class="card-body">
                        <?php if ($success): ?>
                            <div class="alert alert-success">
                                <h5><i class="fas fa-check-circle"></i> Erfolgreich abgemeldet</h5>
                                <p class="mb-0">Sie wurden erfolgreich vom Newsletter abgemeldet. Sie erhalten keine weiteren Newsletter-E-Mails von uns.</p>
                            </div>
                            <div class="text-center">
                                <a href="../index.php" class="btn btn-primary">
                                    <i class="fas fa-home"></i> Zur Startseite
                                </a>
                            </div>
                        <?php else: ?>
                            <?php if ($error): ?>
                                <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
                            <?php endif; ?>
                            
                            <p class="text-muted">Möchten Sie sich vom ByteDohm Newsletter abmelden? Geben Sie einfach Ihre E-Mail-Adresse ein.</p>
                            
                            <form method="POST">
                                <div class="mb-3">
                                    <label for="email" class="form-label">E-Mail-Adresse:</label>
                                    <input type="email" 
                                           class="form-control" 
                                           id="email" 
                                           name="email" 
                                           placeholder="ihre@email.de" 
                                           required
                                           value="<?= htmlspecialchars($_POST['email'] ?? '') ?>">
                                    <div class="form-text">
                                        Geben Sie die E-Mail-Adresse ein, mit der Sie für den Newsletter angemeldet sind.
                                    </div>
                                </div>
                                
                                <div class="d-grid gap-2">
                                    <button type="submit" class="btn btn-warning">
                                        <i class="fas fa-envelope-open"></i> Vom Newsletter abmelden
                                    </button>
                                    <a href="../index.php" class="btn btn-outline-secondary">
                                        <i class="fas fa-arrow-left"></i> Zurück zur Startseite
                                    </a>
                                </div>
                            </form>
                            
                            <hr class="my-4">
                            
                            <div class="alert alert-info">
                                <h6><i class="fas fa-info-circle"></i> Hinweis</h6>
                                <p class="mb-0">
                                    Falls Sie sich umentscheiden, können Sie sich jederzeit wieder für den Newsletter anmelden, 
                                    indem Sie ein Kundenkonto erstellen oder bei der Bestellung das Newsletter-Häkchen setzen.
                                </p>
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