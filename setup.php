<?php
/**
 * ByteDohm.de Setup Script
 * Initialisiert die MySQL-Datenbank und erstellt den Admin-Benutzer
 */

// Database Configuration
$host = '45.88.108.231';
$dbname = 'u6560-6636_bytedohm';
$username = 'u6560-6636_bytedohm';
$password = 'HeikoCindy-8';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    echo "✓ Datenbankverbindung erfolgreich<br>";
} catch(PDOException $e) {
    die("❌ Verbindungsfehler: " . $e->getMessage());
}

// Admin-Benutzer erstellen falls nicht vorhanden
try {
    $stmt = $pdo->prepare("SELECT id FROM admin_users WHERE username = 'admin'");
    $stmt->execute();
    
    if (!$stmt->fetch()) {
        $password_hash = password_hash('admin123', PASSWORD_DEFAULT);
        $stmt = $pdo->prepare("INSERT INTO admin_users (username, email, password_hash, is_active, created_at) VALUES (?, ?, ?, 1, NOW())");
        $stmt->execute(['admin', 'admin@bytedohm.de', $password_hash]);
        echo "✓ Admin-Benutzer erstellt (admin/admin123)<br>";
    } else {
        echo "✓ Admin-Benutzer bereits vorhanden<br>";
    }
} catch(PDOException $e) {
    echo "❌ Fehler beim Erstellen des Admin-Benutzers: " . $e->getMessage() . "<br>";
}

// Testen ob alle Tabellen vorhanden sind
$tables = ['customers', 'orders', 'order_items', 'invoices', 'components', 'prebuilt_pcs', 'configurations', 'admin_users'];
$missing_tables = [];

foreach ($tables as $table) {
    try {
        $stmt = $pdo->query("SELECT 1 FROM $table LIMIT 1");
        echo "✓ Tabelle '$table' vorhanden<br>";
    } catch(PDOException $e) {
        $missing_tables[] = $table;
        echo "❌ Tabelle '$table' fehlt<br>";
    }
}

if (empty($missing_tables)) {
    echo "<br><strong>✅ Setup erfolgreich abgeschlossen!</strong><br>";
    echo "<br>Nächste Schritte:<br>";
    echo "1. Öffnen Sie <a href='index.php'>index.php</a> für die Website<br>";
    echo "2. Öffnen Sie <a href='admin/login.php'>admin/login.php</a> für das Admin-Panel<br>";
    echo "3. Login-Daten: admin / admin123<br>";
} else {
    echo "<br><strong>❌ Setup unvollständig</strong><br>";
    echo "Fehlende Tabellen: " . implode(', ', $missing_tables) . "<br>";
    echo "Bitte führen Sie zuerst die Python-Version aus, um die Datenbank zu initialisieren.<br>";
}
?>