// =====================================================================
//  TON ALGORITHME DE CHIFFREMENT : à coller dans les deux fonctions
// =====================================================================
//  Ce fichier unique est compilé deux fois :
//    - en WebAssembly pour le téléphone  -> compiler_telephone.bat
//    - en DLL pour le PC                 -> compiler_pc.bat
//
//  Règles à respecter :
//    1. Ne change pas le nom ni les paramètres des deux fonctions.
//    2. Les données sont modifiées SUR PLACE : la taille ne doit pas changer.
//    3. dechiffrer(chiffrer(x)) doit redonner exactement x
//       (vérifie-le avec verifier_cpp.bat).
//    4. Pas de lecture de fichier ni d'affichage (pas de cin / cout) :
//       la fonction reçoit les octets et les transforme, c'est tout.
//  Tu peux ajouter d'autres fonctions, des #include, ta clé, etc.
// =====================================================================

#include <cstdint>

#ifdef __EMSCRIPTEN__
  #include <emscripten.h>
  #define EXPORT extern "C" EMSCRIPTEN_KEEPALIVE
#else
  #define EXPORT extern "C" __declspec(dllexport)
#endif

// Appelée sur le TÉLÉPHONE, juste après la prise et la signature
EXPORT void chiffrer(uint8_t* donnees, int taille) {
    // >>> TON CODE ICI <<<
}

// Appelée sur le PC, à la réception, avant la vérification de la signature
EXPORT void dechiffrer(uint8_t* donnees, int taille) {
    // >>> TON CODE ICI <<<
}
