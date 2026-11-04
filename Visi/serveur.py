"""
Photo sécurisée - serveur de démonstration.

Le téléphone prend la photo et la SIGNE immédiatement (clé privée non exportable,
dans le navigateur). Le PC ne fait que recevoir et VÉRIFIER : la moindre
modification de la photo après la prise rend la signature invalide.
"""

import base64
import ctypes
import datetime
import hashlib
import ipaddress
import json
import random
import shutil
import socket
import uuid
from pathlib import Path

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.x509.oid import NameOID
from flask import Flask, abort, jsonify, request, send_file, send_from_directory
from PIL import Image

DOSSIER = Path(__file__).parent
PHOTOS = DOSSIER / "photos"
APPAREILS = DOSSIER / "appareils.json"
CERT = DOSSIER / "cert.pem"
CLE_TLS = DOSSIER / "cle.pem"
PORT = 5000

PHOTOS.mkdir(exist_ok=True)
app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024


# ---------- Outils ----------

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


def empreinte_cle(spki: bytes) -> str:
    h = hashlib.sha256(spki).hexdigest()[:16].upper()
    return " ".join(h[i:i + 4] for i in range(0, 16, 4))


def lire_appareils():
    return json.loads(APPAREILS.read_text("utf-8")) if APPAREILS.exists() else {}


def message_signe(sha256_hex, horodatage, appareil):
    # Exactement le même texte que celui signé par le téléphone (voir telephone.html)
    return f"{sha256_hex}|{horodatage}|{appareil}".encode("utf-8")


def verifier(meta):
    """Recalcule l'empreinte du fichier ACTUEL et vérifie la signature du téléphone."""
    donnees = (PHOTOS / f"{meta['id']}.png").read_bytes()
    empreinte_actuelle = hashlib.sha256(donnees).hexdigest()
    appareil = lire_appareils().get(meta["appareil"])
    resultat = {"empreinte_actuelle": empreinte_actuelle, "appareil_connu": appareil is not None}
    if appareil is None:
        resultat["authentique"] = False
        resultat["raison"] = "Appareil inconnu"
        return resultat
    cle = serialization.load_der_public_key(base64.b64decode(appareil["spki"]))
    sig = base64.b64decode(meta["signature"])
    sig_der = encode_dss_signature(int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:], "big"))
    try:
        cle.verify(sig_der, message_signe(empreinte_actuelle, meta["horodatage"], meta["appareil"]),
                   ec.ECDSA(hashes.SHA256()))
        resultat["authentique"] = True
        resultat["raison"] = "Signature valide : la photo est identique à celle prise par le téléphone"
    except InvalidSignature:
        resultat["authentique"] = False
        resultat["raison"] = "Signature invalide : la photo a été modifiée après la prise"
    resultat["marque_cpp"] = verifier_marque_cpp(PHOTOS / f"{meta['id']}.png")
    if resultat["marque_cpp"] is False:
        resultat["authentique"] = False
        if "valide :" in resultat["raison"]:
            resultat["raison"] = "Signature valide, mais la marque C++ est absente (le téléphone n'a pas appliqué encryptage_0)"
    return resultat


# ======================================================================
#  TON ALGORITHME C++ (cpp/encryptage.h), compilé en marque.dll
# ======================================================================
#  Le téléphone applique encryptage_0 aux pixels AVANT de signer.
#  Ici, on appelle decryptage_0 (via verifier_marque dans cpp/pont.cpp)
#  pour contrôler la marque. Si marque.dll est absente, ce contrôle est ignoré.
DLL = DOSSIER / "marque.dll"
lib_cpp = None
if DLL.exists():
    lib_cpp = ctypes.CDLL(str(DLL))
    lib_cpp.verifier_marque.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
    lib_cpp.verifier_marque.restype = ctypes.c_int


def verifier_marque_cpp(chemin_png):
    """Renvoie True/False selon ton decryptage_0, ou None si la DLL n'est pas là."""
    if lib_cpp is None:
        return None
    img = Image.open(chemin_png).convert("RGBA")
    return lib_cpp.verifier_marque(img.tobytes(), img.width, img.height) == 1
# ======================================================================


def lire_meta(id_photo):
    chemin = PHOTOS / f"{id_photo}.json"
    if not chemin.exists():
        abort(404)
    return json.loads(chemin.read_text("utf-8"))


# ---------- Pages ----------

@app.get("/api/config")
def config():
    # Le téléphone vérifie que le PC sait déchiffrer, pour ne pas envoyer une photo illisible
    return jsonify(marque_cpp=lib_cpp is not None)


@app.get("/")
def page_telephone():
    return send_from_directory("static", "telephone.html")


@app.get("/pc")
def page_pc():
    return send_from_directory("static", "pc.html")


# ---------- API ----------

@app.post("/api/appareil")
def enregistrer_appareil():
    """Le téléphone envoie sa clé PUBLIQUE (la clé privée ne quitte jamais le téléphone)."""
    spki_b64 = request.json["spki"]
    empreinte = empreinte_cle(base64.b64decode(spki_b64))
    appareils = lire_appareils()
    if empreinte not in appareils:
        appareils[empreinte] = {
            "spki": spki_b64,
            "nom": request.json.get("nom", "Téléphone"),
            "enregistre_le": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        APPAREILS.write_text(json.dumps(appareils, indent=2, ensure_ascii=False), "utf-8")
    return jsonify(empreinte=empreinte)


@app.post("/api/photo")
def recevoir_photo():
    id_photo = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    request.files["photo"].save(PHOTOS / f"{id_photo}.png")
    shutil.copy(PHOTOS / f"{id_photo}.png", PHOTOS / f"{id_photo}.original.png")
    meta = {
        "id": id_photo,
        "signature": request.form["signature"],
        "horodatage": request.form["horodatage"],
        "appareil": request.form["appareil"],
        "empreinte_signee": request.form["empreinte"],
        "duree_ms": request.form.get("duree_ms"),
    }
    (PHOTOS / f"{id_photo}.json").write_text(json.dumps(meta, indent=2), "utf-8")
    return jsonify(id=id_photo, **verifier(meta))


@app.get("/api/photos")
def lister_photos():
    resultat = []
    for chemin in sorted(PHOTOS.glob("*.json"), reverse=True):
        meta = json.loads(chemin.read_text("utf-8"))
        resultat.append({**meta, **verifier(meta), "fichier": str(PHOTOS / f"{meta['id']}.png")})
    return jsonify(resultat)


@app.get("/photos/<id_photo>.png")
def servir_photo(id_photo):
    lire_meta(id_photo)
    return send_file(PHOTOS / f"{id_photo}.png", max_age=0)


@app.post("/api/photos/<id_photo>/alterer")
def alterer(id_photo):
    """Démo : change UN SEUL pixel, choisi au hasard à chaque clic.

    Le rouge change de 1 (invisible à l'œil). +1 ou -1 change toujours le reste
    modulo 3, donc la marque est cassée à chaque fois, et comme le pixel change
    à chaque clic, on ne retombe jamais sur la photo d'origine.
    """
    lire_meta(id_photo)
    chemin = PHOTOS / f"{id_photo}.png"
    img = Image.open(chemin).convert("RGB")
    x, y = random.randrange(img.width), random.randrange(img.height)
    r, g, b = img.getpixel((x, y))
    nouveau_r = r + 1 if r < 255 else r - 1
    img.putpixel((x, y), (nouveau_r, g, b))
    img.save(chemin)
    return jsonify(pixel=[x, y], avant=[r, g, b], apres=[nouveau_r, g, b])


@app.post("/api/photos/<id_photo>/restaurer")
def restaurer(id_photo):
    lire_meta(id_photo)
    shutil.copy(PHOTOS / f"{id_photo}.original.png", PHOTOS / f"{id_photo}.png")
    return jsonify(ok=True)


@app.delete("/api/photos")
def tout_effacer():
    for f in PHOTOS.iterdir():
        f.unlink()
    return jsonify(ok=True)


if __name__ == "__main__":
    ips = adresses_locales()
    creer_certificat(ips)
    print("\n=== Photo sécurisée - démo ===")
    print("  Vérification C++ :", "ACTIVE (marque.dll chargée)" if lib_cpp else "inactive (pas de marque.dll)")
    print(f"  Écran de vérification (sur ce PC) : https://localhost:{PORT}/pc")
    for ip in ips:
        if ip != "127.0.0.1":
            print(f"  Sur le téléphone (même Wi-Fi)     : https://{ip}:{PORT}")
    print("  (Accepte l'avertissement de certificat : il est normal, le certificat est local)\n")
    app.run(host="0.0.0.0", port=PORT, ssl_context=(str(CERT), str(CLE_TLS)), threaded=True)
