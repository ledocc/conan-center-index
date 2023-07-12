#include <iostream>

#include <keychain.h>


int main(void) {

    std::cout << QKeychain::isAvailable();

    return 0;
}
