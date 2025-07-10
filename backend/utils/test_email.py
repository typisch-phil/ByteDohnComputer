#!/usr/bin/env python3
"""
E-Mail Test Script für ByteDohm
Testet die E-Mail-Funktionalität direkt
"""

import os
import sys
from email_service import EmailService

def test_email_service():
    """Teste den E-Mail-Service"""
    print("=== E-MAIL SERVICE TEST ===")
    
    # E-Mail Service initialisieren
    email_service = EmailService()
    
    print(f"SMTP Server: {email_service.smtp_server}")
    print(f"SMTP Port: {email_service.smtp_port}")
    print(f"SMTP Username: {email_service.smtp_username}")
    print(f"From Email: {email_service.sender_email}")
    
    # Test-E-Mail senden
    test_email = "test@bytedohm.de"  # Ändern Sie diese zu Ihrer Test-E-Mail
    subject = "ByteDohm E-Mail Test"
    html_body = """
    <html>
    <body>
        <h2>ByteDohm E-Mail Test</h2>
        <p>Dies ist eine Test-E-Mail vom ByteDohm E-Mail-System.</p>
        <p>Wenn Sie diese E-Mail erhalten, funktioniert das System korrekt.</p>
        <hr>
        <small>ByteDohm.de - Ihr PC-Konfigurator</small>
    </body>
    </html>
    """
    
    text_body = """
    ByteDohm E-Mail Test
    
    Dies ist eine Test-E-Mail vom ByteDohm E-Mail-System.
    Wenn Sie diese E-Mail erhalten, funktioniert das System korrekt.
    
    ByteDohm.de - Ihr PC-Konfigurator
    """
    
    print(f"\nSende Test-E-Mail an: {test_email}")
    success = email_service._send_email(test_email, subject, html_body, text_body)
    
    if success:
        print("✅ E-Mail-Test ERFOLGREICH!")
    else:
        print("❌ E-Mail-Test FEHLGESCHLAGEN!")
    
    return success

if __name__ == "__main__":
    test_email_service()