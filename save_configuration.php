<?php
require_once 'config.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    try {
        $name = $input['name'];
        $components = json_encode($input['components']);
        $total_price = $input['total_price'];
        $customer_id = $_SESSION['customer_id'] ?? null;
        
        if (!$name || !$components || !$total_price) {
            throw new Exception('Unvollständige Daten');
        }
        
        $stmt = $pdo->prepare("INSERT INTO configurations (name, components, total_price, customer_id, created_at) VALUES (?, ?, ?, ?, NOW())");
        $stmt->execute([$name, $components, $total_price, $customer_id]);
        
        echo json_encode(['success' => true, 'message' => 'Konfiguration gespeichert']);
        
    } catch (Exception $e) {
        echo json_encode(['success' => false, 'message' => $e->getMessage()]);
    }
} else {
    echo json_encode(['success' => false, 'message' => 'Ungültige Anfrage']);
}
?>