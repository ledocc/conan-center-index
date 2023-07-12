#include <cstdlib>
#include <iostream>
#include <qgis/qgsvector.h>


int main(void) {

  QgsVector vector{10.0, 10.0};
  auto length = vector.length();

  std::cout << "vector length = " << length;
  
  return 0;
}
