#include <CImg.h>
#include <stdlib.h>

int decallage_0(int i){
    return i%3;
}


cimg_library::CImg<int> encryptage_0(cimg_library::CImg<int> photo){

    int* pixel = photo.data();

    for(int i = 0; i < photo.size(); i++){
        pixel[i] = 0;
    }

    return photo;
}

bool decryptage_0(cimg_library::CImg<int> photo){


    return 0;
}


int main(){
    cimg_library::CImg<float> photo("../photo.jpg");

    std::cout << photo.pixel_type() << std::endl;

    photo.display();
    encryptage_0(photo);
    photo.display();

    decryptage_0(photo);

    return 0;
}