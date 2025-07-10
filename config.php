<?php
// ByteDohm.de - Database Configuration
$host = '45.88.108.231';
$dbname = 'u6560-6636_bytedohm';
$username = 'u6560-6636_bytedohm';
$password = 'HeikoCindy-8';

// Email Configuration
$smtp_server = 'mail.bytedohm.de';
$smtp_port = 465;
$smtp_username = 'noreply@bytedohm.de';
$smtp_password = 'noreplypassword';

// Stripe Configuration
$stripe_secret_key = 'sk_test_...'; // Aus Umgebungsvariablen laden

// DHL Configuration
$dhl_username = 'your_dhl_username';
$dhl_password = 'your_dhl_password';
$dhl_ekp = 'your_ekp_number';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    die("Verbindungsfehler: " . $e->getMessage());
}

// Session-Konfiguration
ini_set('session.cookie_httponly', 1);
ini_set('session.use_only_cookies', 1);
ini_set('session.cookie_secure', 1);
session_start();
?>