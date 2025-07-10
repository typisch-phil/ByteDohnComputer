<?php require_once '../config.php'; ?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AGB - ByteDohm.de</title>
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

    <div class="container mt-5 pt-4">
        <div class="row">
            <div class="col-12">
                <h1>Allgemeine Geschäftsbedingungen</h1>
                <p class="text-muted">Stand: <?= date('d.m.Y') ?></p>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-body">
                        <h3>§ 1 Geltungsbereich</h3>
                        <p>Diese Allgemeinen Geschäftsbedingungen gelten für alle Bestellungen über den Online-Shop von ByteDohm.de.</p>

                        <h3>§ 2 Vertragspartner</h3>
                        <p>Der Kaufvertrag kommt zustande mit:<br>
                        ByteDohm.de<br>
                        [Ihre Adresse]<br>
                        [Ihre Stadt]</p>

                        <h3>§ 3 Vertragsschluss</h3>
                        <p>Die Darstellung der Produkte im Online-Shop stellt kein bindendes Angebot dar. Durch Anklicken des Buttons "Jetzt bestellen" geben Sie eine verbindliche Bestellung ab. Der Kaufvertrag kommt durch die Bestätigung der Bestellung durch ByteDohm.de zustande.</p>

                        <h3>§ 4 Preise und Zahlungsbedingungen</h3>
                        <p>Alle Preise verstehen sich inklusive der gesetzlichen Mehrwertsteuer. Als Kleinunternehmer im Sinne von § 19 Abs. 1 UStG wird keine Umsatzsteuer berechnet. Die Zahlung erfolgt über Stripe.</p>

                        <h3>§ 5 Lieferung</h3>
                        <p>Die Lieferung erfolgt an die vom Kunden angegebene Lieferadresse. Die Lieferzeit beträgt in der Regel 3-7 Werktage. Die Lieferung erfolgt durch DHL.</p>

                        <h3>§ 6 Widerrufsrecht</h3>
                        <p>Verbrauchern steht ein Widerrufsrecht gemäß den gesetzlichen Bestimmungen zu. Einzelheiten finden Sie in unserer Widerrufsbelehrung.</p>

                        <h3>§ 7 Gewährleistung</h3>
                        <p>Es gelten die gesetzlichen Gewährleistungsbestimmungen. Für Unternehmer wird die Gewährleistung auf ein Jahr begrenzt.</p>

                        <h3>§ 8 Datenschutz</h3>
                        <p>Der Schutz Ihrer persönlichen Daten ist uns wichtig. Einzelheiten zur Datenverarbeitung finden Sie in unserer Datenschutzerklärung.</p>

                        <h3>§ 9 Schlussbestimmungen</h3>
                        <p>Es gilt deutsches Recht. Sollten einzelne Bestimmungen unwirksam sein, bleibt die Wirksamkeit der übrigen Bestimmungen unberührt.</p>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Rechtliche Hinweise</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled">
                            <li><a href="agb.php">AGB</a></li>
                            <li><a href="datenschutz.php">Datenschutz</a></li>
                            <li><a href="widerruf.php">Widerrufsrecht</a></li>
                            <li><a href="zahlungsmethoden.php">Zahlungsmethoden</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>