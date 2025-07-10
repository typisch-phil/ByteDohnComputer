<?php
require_once 'config.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($_SESSION['cart'])) {
        $_SESSION['cart'] = [];
    }
    
    try {
        if ($input['type'] === 'custom') {
            // Custom PC Konfiguration
            $cart_item = [
                'type' => 'custom',
                'name' => 'Custom PC Konfiguration',
                'price' => $input['total_price'],
                'quantity' => 1,
                'components' => $input['components']
            ];
        } elseif ($input['type'] === 'prebuilt') {
            // Prebuilt PC
            $cart_item = [
                'type' => 'prebuilt',
                'id' => $input['id'],
                'name' => $input['name'],
                'price' => $input['price'],
                'quantity' => $input['quantity'] ?? 1
            ];
        } else {
            throw new Exception('Ungültiger Produkttyp');
        }
        
        $_SESSION['cart'][] = $cart_item;
        
        echo json_encode(['success' => true, 'message' => 'Artikel zum Warenkorb hinzugefügt']);
        
    } catch (Exception $e) {
        echo json_encode(['success' => false, 'message' => $e->getMessage()]);
    }
} else {
    echo json_encode(['success' => false, 'message' => 'Ungültige Anfrage']);
}
?>