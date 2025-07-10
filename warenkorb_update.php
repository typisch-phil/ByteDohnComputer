<?php
require_once 'config.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($_SESSION['cart'])) {
        $_SESSION['cart'] = [];
    }
    
    try {
        $action = $input['action'];
        $index = $input['index'];
        
        if ($action === 'update_quantity') {
            $change = $input['change'];
            if (isset($_SESSION['cart'][$index])) {
                $_SESSION['cart'][$index]['quantity'] += $change;
                
                // Mindestmenge 1
                if ($_SESSION['cart'][$index]['quantity'] < 1) {
                    $_SESSION['cart'][$index]['quantity'] = 1;
                }
            }
        } elseif ($action === 'remove_item') {
            if (isset($_SESSION['cart'][$index])) {
                unset($_SESSION['cart'][$index]);
                $_SESSION['cart'] = array_values($_SESSION['cart']); // Array neu indizieren
            }
        }
        
        echo json_encode(['success' => true]);
        
    } catch (Exception $e) {
        echo json_encode(['success' => false, 'message' => $e->getMessage()]);
    }
} else {
    echo json_encode(['success' => false, 'message' => 'Ungültige Anfrage']);
}
?>