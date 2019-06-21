#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv){
    int offsets[7];
    int odix = (sizeof(argv[1]) >> 10) & 7;
    if (offsets[odix] < 0){
        return 1;
    }
    return 0;
}
