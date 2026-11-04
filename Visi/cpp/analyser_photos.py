"""
Contrôle indépendant : vérifie, sans passer par ton C++, que les photos reçues
respectent bien la règle de ton algorithme (R%3 == 0, G%3 == 1, B%3 == 2).

  - photo non marquée : environ 33 % des valeurs respectent la règle (hasard)
  - photo marquée par encryptage_0 : 100 %
"""
import sys
from pathlib import Path

from PIL import Image

PHOTOS = Path(__file__).resolve().parent.parent / "photos"
fichiers = [Path(f) for f in sys.argv[1:]] or sorted(
    f for f in PHOTOS.glob("*.png") if not f.name.endswith(".original.png"))
if not fichiers:
    sys.exit("Aucune photo dans le dossier photos/")

for f in fichiers:
    img = Image.open(f).convert("RGB")
    octets = img.tobytes()
    r, g, b = octets[0::3], octets[1::3], octets[2::3]
    n = len(r)
    pr = sum(v % 3 == 0 for v in r) / n * 100
    pg = sum(v % 3 == 1 for v in g) / n * 100
    pb = sum(v % 3 == 2 for v in b) / n * 100
    fautifs = n - sum(x % 3 == 0 and y % 3 == 1 and z % 3 == 2 for x, y, z in zip(r, g, b))
    verdict = "✅ MARQUÉE" if fautifs == 0 else ("❌ non marquée" if min(pr, pg, pb) < 90 else "⚠️ marquée puis modifiée")
    print(f"{f.name}\n   rouge%3=0 : {pr:5.1f} %   vert%3=1 : {pg:5.1f} %   bleu%3=2 : {pb:5.1f} %"
          f"\n   pixels hors règle : {fautifs} / {n}   -> {verdict}\n")
