<?php
session_start();

// Admin Session-Daten löschen
unset($_SESSION['admin_id']);
unset($_SESSION['admin_username']);
unset($_SESSION['admin_email']);

// Zur Login-Seite weiterleiten
header('Location: login.php');
exit;
?>