<?php
require_once '../config.php';

$error = '';
$success = '';

if ($_POST) {
    $email = $_POST['email'] ?? '';
    $password = $_POST['password'] ?? '';
    $password_confirm = $_POST['password_confirm'] ?? '';
    $first_name = $_POST['first_name'] ?? '';
    $last_name = $_POST['last_name'] ?? '';
    $newsletter = isset($_POST['newsletter']) ? 1 : 0;
    
    if (!$email || !$password || !$first_name || !$last_name) {
        $error = 'Bitte füllen Sie alle Pflichtfelder aus.';
    } elseif ($password !== $password_confirm) {
        $error = 'Die Passwörter stimmen nicht überein.';
    } elseif (strlen($password) < 6) {
        $error = 'Das Passwort muss mindestens 6 Zeichen lang sein.';
    } else {
        // Prüfen ob E-Mail bereits existiert
        $stmt = $pdo->prepare("SELECT id FROM customers WHERE email = ?");
        $stmt->execute([$email]);
        if ($stmt->fetch()) {
            $error = 'Diese E-Mail-Adresse ist bereits registriert.';
        } else {
            // Neuen Kunden erstellen
            $password_hash = password_hash($password, PASSWORD_DEFAULT);
            $stmt = $pdo->prepare("INSERT INTO customers (email, password_hash, first_name, last_name, newsletter_subscription, created_at) VALUES (?, ?, ?, ?, ?, NOW())");
            
            if ($stmt->execute([$email, $password_hash, $first_name, $last_name, $newsletter])) {
                $customer_id = $pdo->lastInsertId();
                
                // Automatisch anmelden
                $_SESSION['customer_id'] = $customer_id;
                $_SESSION['customer_email'] = $email;
                $_SESSION['customer_name'] = $first_name . ' ' . $last_name;
                
                // Willkommens-E-Mail senden (vereinfacht)
                // send_registration_email($customer_id);
                
                header('Location: dashboard.php');
                exit;
            } else {
                $error = 'Fehler bei der Registrierung. Bitte versuchen Sie es erneut.';
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrieren - ByteDohm.de</title>
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
                    <div class="card-header">
                        <h4 class="mb-0"><i class="fas fa-user-plus"></i> Registrieren</h4>
                    </div>
                    <div class="card-body">
                        <?php if ($error): ?>
                            <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
                        <?php endif; ?>
                        
                        <form method="POST">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="first_name" class="form-label">Vorname *</label>
                                        <input type="text" class="form-control" id="first_name" name="first_name" required
                                               value="<?= htmlspecialchars($_POST['first_name'] ?? '') ?>">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="last_name" class="form-label">Nachname *</label>
                                        <input type="text" class="form-control" id="last_name" name="last_name" required
                                               value="<?= htmlspecialchars($_POST['last_name'] ?? '') ?>">
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="email" class="form-label">E-Mail-Adresse *</label>
                                <input type="email" class="form-control" id="email" name="email" required
                                       value="<?= htmlspecialchars($_POST['email'] ?? '') ?>">
                            </div>
                            
                            <div class="mb-3">
                                <label for="password" class="form-label">Passwort *</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                                <div class="form-text">Mindestens 6 Zeichen</div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="password_confirm" class="form-label">Passwort bestätigen *</label>
                                <input type="password" class="form-control" id="password_confirm" name="password_confirm" required>
                            </div>
                            
                            <div class="mb-3 form-check">
                                <input type="checkbox" class="form-check-input" id="newsletter" name="newsletter"
                                       <?= isset($_POST['newsletter']) ? 'checked' : '' ?>>
                                <label class="form-check-label" for="newsletter">
                                    Newsletter abonnieren (optional)
                                </label>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-user-plus"></i> Registrieren
                                </button>
                            </div>
                        </form>
                        
                        <hr>
                        
                        <div class="text-center">
                            <p class="mb-0">Bereits registriert? 
                                <a href="login.php">Hier anmelden</a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>