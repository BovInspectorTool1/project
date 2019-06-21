#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct ftype{
    int majtype;
    int type;
} sftype;

int main(int argc, char** argv){
    sftype* t = (sftype*)malloc(sizeof(sftype));
    char end[10];
    if (sscanf (argv[1], "%d %d %s", &t->majtype, &t->type, end) != 3)
    {
        return 1;
    }
    return 0;
}
