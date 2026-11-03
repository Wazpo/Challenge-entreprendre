#include <CImg.h>

int decallage_0(int i){
    return i%3;
}


cimg_library::CImg<int> encryptage_0(cimg_library::CImg<int> photo){
    photo.front();

    return photo;
}

bool decryptage_0(cimg_library::CImg<int> photo){


    return 0;
}


int main(){
    cimg_library::CImg<int> photo("photo.jpg");

    encryptage_0(photo);
    decryptage_0(photo);

    return 0;
}