#include <CImg.h>
#include <stdlib.h>
#include <iostream>
#include <string>

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


int main(){
    const char* path_photo = "../photo1.jpg";
    const char* path_photo_cryptee = "../photo1_cryptee.jpg";
    cimg_library::CImg<unsigned char> photo(path_photo);

    // photo.display();
    std::cout << "Décryptage de l'image non cryptée : " << decryptage_0(photo) << std::endl;

    encryptage_0(photo);

    // photo.display();
    std::cout << "Décryptage de l'image cryptée : " << decryptage_0(photo) << std::endl;

    photo.save(path_photo_cryptee, -1, 9);

    return 0;
}