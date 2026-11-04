// Ton algorithme (copié tel quel depuis ton main.cpp).
// Utilisé à la fois par main.cpp (ligne de commande) et par pont.cpp (téléphone + PC).
#pragma once
#include "CImg.h"

int decallage_0(int i){
    return i%3;
}


cimg_library::CImg<unsigned char> encryptage_0(cimg_library::CImg<unsigned char> & photo){
    for(int x = 0; x < photo.width(); x++)
    for(int y = 0; y < photo.height(); y++)
    for(int c = 0; c < photo.spectrum(); c++){
        unsigned char* pointp = photo.data(x, y, 0, c);
        int point = *pointp;
        // On met la coordonnée rouge 0 modulo 3
        if(c == 0){
            if(point%3 == 1) point -= 1;
            if(point%3 == 2) point += 1;
        }
        // On met la coordonnée rouge 1 modulo 3
        if(c == 1){
            if(point%3 == 0) point += 1;
            if(point%3 == 2) point -= 1;
        }
        // On met la coordonnée rouge 2 modulo 3
        if(c == 2){
            if(point%3 == 0) point -= 1;
            if(point%3 == 1) point += 1;
        }

        if(point < 0) point += 3;
        if(point > 255) point -= 3;
        *pointp = point;
    }

    return photo;
}

bool decryptage_0(cimg_library::CImg<unsigned char> & photo){
    for(int x = 0; x < photo.width(); x++)
    for(int y = 0; y < photo.height(); y++)
    for(int c = 0; c < photo.spectrum(); c++){
        unsigned char* point = photo.data(x, y, 0, c);
        // On met la coordonnée rouge 0 modulo 3
        if(c == 0 && (*point%3 != 0)) return false;
        // On met la coordonnée rouge 1 modulo 3
        if(c == 1 && (*point%3 != 1)) return false;
        // On met la coordonnée rouge 2 modulo 3
        if(c == 2 && (*point%3 != 2)) return false;
    }

    return true;
}
