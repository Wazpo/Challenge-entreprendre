// =====================================================================
//  PONT entre ton algorithme (encryptage.h) et l'application
// =====================================================================
//  Le navigateur et Python manipulent les pixels sous forme d'un tableau
//  RGBA : [R,G,B,A, R,G,B,A, ...], ligne par ligne.
//  Ces fonctions copient ce tableau dans une image CImg, appellent TES
//  fonctions encryptage_0 / decryptage_0, puis recopient le résultat.
//
//  Pour changer d'algorithme : modifie encryptage.h, pas ce fichier.
// =====================================================================
#include <cstdint>
#include "encryptage.h"

#ifdef __EMSCRIPTEN__
  #include <emscripten.h>
  #define EXPORT extern "C" EMSCRIPTEN_KEEPALIVE
#else
  #define EXPORT extern "C" __declspec(dllexport)
#endif

static cimg_library::CImg<unsigned char> vers_cimg(const uint8_t* rgba, int largeur, int hauteur) {
    cimg_library::CImg<unsigned char> img(largeur, hauteur, 1, 4);
    for (int y = 0; y < hauteur; y++)
    for (int x = 0; x < largeur; x++)
    for (int c = 0; c < 4; c++)
        img(x, y, 0, c) = rgba[(y * largeur + x) * 4 + c];
    return img;
}

// TÉLÉPHONE : appliquée à la photo juste après la prise, AVANT la signature
EXPORT void marquer(uint8_t* rgba, int largeur, int hauteur) {
    cimg_library::CImg<unsigned char> img = vers_cimg(rgba, largeur, hauteur);
    encryptage_0(img);
    for (int y = 0; y < hauteur; y++)
    for (int x = 0; x < largeur; x++)
    for (int c = 0; c < 4; c++)
        rgba[(y * largeur + x) * 4 + c] = img(x, y, 0, c);
}

// PC : renvoie 1 si la marque est intacte, 0 sinon
EXPORT int verifier_marque(const uint8_t* rgba, int largeur, int hauteur) {
    cimg_library::CImg<unsigned char> img = vers_cimg(rgba, largeur, hauteur);
    return decryptage_0(img) ? 1 : 0;
}
