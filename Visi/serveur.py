"""
Photo sécurisée - serveur de démonstration.

Ce serveur sert UNIQUEMENT à afficher la page sur le téléphone en HTTPS
(le navigateur l'exige pour la caméra et la cryptographie).
Le téléphone signe, range et vérifie ses photos lui-même : rien n'est envoyé ici.
"""

import datetime
import ipaddress
import socket
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from flask import Flask, send_from_directory

DOSSIER = Path(__file__).parent
CERT = DOSSIER / "cert.pem"
CLE_TLS = DOSSIER / "cle.pem"
PORT = 5000

app = Flask(__name__, static_folder="static")


def adresses_locales():
    ips = {"127.0.0.1"}
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # aucun paquet envoyé, sert juste à trouver l'IP Wi-Fi
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        ips.update(socket.gethostbyname_ex(socket.gethostname())[2])
    except OSError:
        pass
    return sorted(ips)


def creer_certificat(ips):
    """Certificat HTTPS auto-signé : le navigateur exige HTTPS pour la caméra et la cryptographie."""
    cle = ec.generate_private_key(ec.SECP256R1())
    nom = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Photo securisee (demo)")])
    maintenant = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(nom).issuer_name(nom)
        .public_key(cle.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(maintenant - datetime.timedelta(days=1))
        .not_valid_after(maintenant + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName(
            [x509.DNSName("localhost")] + [x509.IPAddress(ipaddress.ip_address(ip)) for ip in ips]
        ), critical=False)
        .sign(cle, hashes.SHA256())
    )
    CERT.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    CLE_TLS.write_bytes(cle.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    ))


@app.get("/")
def page_telephone():
    return send_from_directory("static", "telephone.html")


if __name__ == "__main__":
    ips = adresses_locales()
    creer_certificat(ips)
    print("\n=== Photo sécurisée - démo ===")
    for ip in ips:
        if ip != "127.0.0.1":
            print(f"  Sur le téléphone (même Wi-Fi) : https://{ip}:{PORT}")
    print("  (Accepte l'avertissement de certificat : il est normal, le certificat est local)")
    print("  Aucune photo n'est envoyée à ce PC : tout reste sur le téléphone.\n")
    app.run(host="0.0.0.0", port=PORT, ssl_context=(str(CERT), str(CLE_TLS)), threaded=True)
