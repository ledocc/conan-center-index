#include <cstdlib>
#include <QDebug>
#include <Qsci/qscilexerjson.h>


int main(void) {

    QsciLexerJSON obj;
    qDebug() << obj.language();

    return EXIT_SUCCESS;
}
