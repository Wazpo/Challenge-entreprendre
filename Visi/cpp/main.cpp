#include "encryptage.h"
#include <stdlib.h>
#include <iostream>
#include <string>

int main(int argc, char* argv[]){
    if(argc < 2){
        std::cout <<
        "Nombre incorrect d'arguments." << std::endl <<
        "[Usage :] ./main $n $file0 ($file1)" << std::endl <<
        "   Si n vaut 0 , lance le cryptage du fichier file0 dans le fichier file1. Sinon Vérifie la certification du fichier file1." << std::endl;
        return 1;
    }
    int encdec = std::atoi(argv[1]);

    if(!encdec){
        if(argc < 4){
            std::cout <<
            "Nombre incorrect d'arguments." << std::endl <<
            "[Usage :] ./main $n $file0 ($file1)" << std::endl <<
            "   Si n vaut 0 , lance le cryptage du fichier file0 dans le fichier file1. Sinon Vérifie la certification du fichier file1." << std::endl;
            return 1;
        }
        const char* path_photo = argv[2];
        const char* path_photo_cryptee = argv[3];

        cimg_library::CImg<unsigned char> photo(path_photo);
        photo = encryptage_0(photo);
        photo.save(path_photo_cryptee, -1, 9);
    }
    else{
        if(argc < 3){
            std::cout <<
            "Nombre incorrect d'arguments." << std::endl <<
            "[Usage :] ./main $n $file0 ($file1)" << std::endl <<
            "   Si n vaut 0 , lance le cryptage du fichier file0 dans le fichier file1. Sinon Vérifie la certification du fichier file1." << std::endl;
            return 1;
        }
        const char* path_photo_cryptee = argv[2];
        cimg_library::CImg<unsigned char> photo_cryptee(path_photo_cryptee);
        std::cout << "Décryptage de l'image : " << (decryptage_0(photo_cryptee) ? "certifiée" : "non-certifiée") << std::endl;
    }

    return 0;
}