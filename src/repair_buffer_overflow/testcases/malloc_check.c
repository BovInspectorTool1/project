#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv){
    char* p = (char*)malloc(sizeof(argv[1]));
    printf("%s",p);
}
