# Photo sécurisée : démonstration

Le téléphone **signe la photo au moment même de la prise** (en quelques millisecondes, avant qu'elle soit enregistrée nulle part).
Le PC vérifie la signature : si la photo est modifiée après la prise, même d'un seul pixel, la vérification échoue.

## Lancer
1. Double-clique sur `lancer.bat`. La première fois, Windows demande d'autoriser Python sur le réseau : accepte pour les **réseaux privés**.
2. Sur le PC, ouvre l'adresse `https://localhost:5000/pc` (l'écran de vérification).
3. Sur le téléphone, connecté au **même Wi-Fi**, ouvre l'adresse `https://<IP>:5000` affichée dans la fenêtre du serveur.
4. Le navigateur affiche un avertissement de certificat. C'est normal, car le certificat est créé localement :
   - Chrome : « Paramètres avancés » puis « Continuer vers le site »
   - Safari : « Afficher les détails » puis « Visiter ce site web »
5. Autorise la caméra, puis prends une photo. Elle apparaît sur le PC avec ✅.

## La démo
- Clique sur **« Modifier 1 pixel »** : la couleur d'un seul pixel change d'une valeur infime, invisible à l'œil, et la photo passe aussitôt en ❌. Les caractères de l'empreinte qui ont changé s'affichent en rouge.
- Tu peux aussi ouvrir le fichier (dans `photos/`) avec Paint, le retoucher, l'enregistrer : l'écran se met à jour tout seul.
- **« Restaurer l'original »** remet la photo d'origine, qui repasse en ✅.

## Principe
1. Le téléphone crée une paire de clés ECDSA P-256. La clé privée est **non exportable** : elle reste dans le navigateur et ne peut pas être lue, même par le code de la page.
2. À la prise : image du capteur → PNG en mémoire → empreinte SHA-256 → signature de `empreinte|date|appareil`.
3. Le PC ne connaît que la clé publique. Il recalcule l'empreinte du fichier tel qu'il est maintenant et vérifie la signature.

## Limites (bon à dire en présentation)
- Si quelqu'un contrôle le téléphone, il peut injecter une fausse image dans la caméra, ou simplement photographier un écran.
- Les solutions professionnelles signent dans une puce sécurisée du téléphone et suivent le standard **C2PA**.

## Ton algorithme C++ (dossier `cpp/`)
| Fichier | Rôle |
|---|---|
| `encryptage.h` | **Ton algorithme** (`encryptage_0`, `decryptage_0`) : c'est le seul fichier à modifier |
| `main.cpp` | Ton programme en ligne de commande, qui utilise `encryptage.h` |
| `pont.cpp` | Relie ton algorithme à l'application (ne pas modifier) |

Où il est appelé :
- **Téléphone** : `encryptage_0` est appliqué aux pixels juste après la prise, **avant** la signature.
- **PC** : `decryptage_0` vérifie la marque. Le résultat s'affiche sur l'écran du PC, à la ligne « Marque C++ ».

### Installer les compilateurs (une seule fois)
```
scoop install mingw
git clone https://github.com/emscripten-core/emsdk C:\emsdk
C:\emsdk\emsdk install latest
C:\emsdk\emsdk activate latest --permanent
```
Ferme puis rouvre le terminal après l'installation.

### Compiler et vérifier
1. `cpp\compiler_pc.bat` : crée `marque.dll`, utilisée par le PC.
2. `cpp\verifier_cpp.bat` : teste ton algorithme seul, sans téléphone. Les 3 lignes doivent être ✅.
3. `cpp\compiler_telephone.bat` : crée `static\marque.js` et `static\marque.wasm`, utilisés par le téléphone.
4. Relance `lancer.bat` (la fenêtre doit afficher « Vérification C++ : ACTIVE »), puis recharge la page sur le téléphone (l'en-tête doit afficher « 🔐 marque C++ active »).
5. Prends une photo. Sur le PC, tu dois voir ✅ Photo authentique et ✅ Marque C++ certifiée. Avec « Modifier 1 pixel », les deux lignes passent en ❌.
