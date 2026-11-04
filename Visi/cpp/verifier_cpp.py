"""Teste marque.dll avec ton algorithme, sans téléphone."""
import ctypes, os, sys
from pathlib import Path

dll = Path(__file__).resolve().parent.parent / "marque.dll"
if not dll.exists():
    sys.exit("❌ marque.dll introuvable : lance d'abord compiler_pc.bat")
lib = ctypes.CDLL(str(dll))
lib.marquer.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
lib.verifier_marque.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]

L, H = 640, 480
def image_aleatoire():
    px = bytearray(os.urandom(L * H * 4))
    px[3::4] = b"\xff" * (L * H)  # alpha opaque, comme une photo
    return px

def marquee(px):
    t = ctypes.create_string_buffer(bytes(px), len(px)); lib.marquer(t, L, H); return bytearray(t.raw[:len(px)])

def verifie(px):
    return lib.verifier_marque(bytes(px), L, H) == 1

ok = True
def test(nom, attendu, obtenu):
    global ok
    bon = attendu == obtenu; ok &= bon
    print(f"{'✅' if bon else '❌'} {nom:45} attendu {attendu}, obtenu {obtenu}")

brute = image_aleatoire()
test("photo non marquée -> refusée", False, verifie(brute))
m = marquee(brute)
test("photo marquée -> acceptée", True, verifie(m))
retouche = bytearray(m); retouche[(240 * L + 320) * 4] ^= 1
test("photo marquée puis 1 pixel modifié -> refusée", False, verifie(retouche))
print("\nRÉSULTAT :", "✅ ton algorithme fonctionne via la DLL" if ok else "❌ problème")
