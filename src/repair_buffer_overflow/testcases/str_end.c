#include <stdio.h>
#include <string.h>


int main(int argc, char** argv){
    char error[20];
    char cmdbuf[20];
    strcpy(cmdbuf, argv[1]);
    sprintf(error, "version does not match latd version ", cmdbuf);
    printf("%s, %s", error, cmdbuf);
}
