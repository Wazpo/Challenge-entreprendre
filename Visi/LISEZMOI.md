# Photo sécurisée : démonstration

Le téléphone **signe la photo au moment même de la prise** (en quelques millisecondes, avant qu'elle soit enregistrée nulle part).
La signature est rangée **dans le fichier PNG lui-même**. Le téléphone garde la photo et peut vérifier à tout moment qu'elle est certifiée : si elle est modifiée, même d'un seul pixel, la vérification échoue.
**Rien n'est envoyé au PC** : il sert seulement à afficher la page sur le téléphone.

## Lancer
1. Double-clique sur `lancer.bat`. La première fois, Windows demande d'autoriser Python sur le réseau : accepte pour les **réseaux privés**.
2. Sur le téléphone, connecté au **même Wi-Fi**, ouvre l'adresse `https://<IP>:5000` affichée dans la fenêtre du serveur.
3. Le navigateur affiche un avertissement de certificat. C'est normal, car le certificat est créé localement :
   - Chrome : « Paramètres avancés » puis « Continuer vers le site »
   - Safari : « Afficher les détails » puis « Visiter ce site web »
4. Autorise la caméra, puis prends une photo. Elle est rangée sur le téléphone.
5. Onglet **🔍 Vérifier** : la photo s'affiche avec ✅ Photo certifiée.

## La démo (onglet Vérifier)
- **« Modifier 1 pixel »** : la couleur d'un seul pixel change d'une valeur infime, invisible à l'œil, et la photo passe aussitôt en ❌. Les caractères de l'empreinte qui ont changé s'affichent en rouge.
- **« Restaurer »** remet la photo d'origine, qui repasse en ✅.
- **« 💾 Enregistrer »** télécharge le fichier PNG certifié. **« Vérifier un fichier PNG… »** permet de le revérifier plus tard, ou de tester un fichier retouché.

## Principe
1. Le téléphone crée **une seule clé secrète** (HMAC-SHA256), **non exportable** : elle reste dans le navigateur et ne peut pas être lue, même par le code de la page. Elle sert à signer et à vérifier.
2. À la prise : image du capteur → marque C++ → PNG en mémoire → empreinte SHA-256 → signature de `empreinte|date|appareil`.
3. La signature est glissée dans le PNG, dans un bloc texte `visi-certificat`. L'image n'est pas touchée.
4. Pour vérifier, on retire ce bloc, on recalcule l'empreinte et on contrôle la signature avec la clé de l'appareil.

## Limites (bon à dire en présentation)
- **Seul l'appareil qui a pris la photo peut la vérifier**, car lui seul possède la clé. Pour qu'une autre personne puisse vérifier, il faudrait une paire de clés (clé privée pour signer, clé publique pour vérifier).
- **Si on efface les données du navigateur, la clé est perdue** et les anciennes photos ne peuvent plus être vérifiées.
- Envoyer la photo par une messagerie (WhatsApp, etc.) la recompresse en JPEG : elle n'est alors plus certifiée.
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
- **Téléphone, onglet Vérifier** : `decryptage_0` contrôle la marque. Le résultat s'affiche à la ligne « Marque C++ ».

### Installer les compilateurs (une seule fois)
```
scoop install mingw
git clone https://github.com/emscripten-core/emsdk C:\emsdk
C:\emsdk\emsdk install latest
C:\emsdk\emsdk activate latest --permanent
```
Ferme puis rouvre le terminal après l'installation.

### Compiler et vérifier
1. `cpp\compiler_pc.bat` : crée `marque.dll`, utilisée seulement par le test de l'étape 2.
2. `cpp\verifier_cpp.bat` : teste ton algorithme seul, sans téléphone. Les 3 lignes doivent être ✅.
3. `cpp\compiler_telephone.bat` : crée `static\marque.js` et `static\marque.wasm`, utilisés par le téléphone.
4. Relance `lancer.bat`, puis recharge la page sur le téléphone (l'en-tête doit afficher « 🔐 marque C++ active »).
5. Prends une photo. Dans l'onglet Vérifier, tu dois voir ✅ Photo certifiée et ✅ Marque C++ intacte. Avec « Modifier 1 pixel », les deux lignes passent en ❌.
