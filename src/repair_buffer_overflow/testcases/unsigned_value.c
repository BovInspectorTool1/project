#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv){
    int ilen;
    for (int i = 0; i < 10; i++){
        ilen = sizeof(argv[1]);
        if (ilen > 65534)
            return 0;
    }
    return 1;
}
