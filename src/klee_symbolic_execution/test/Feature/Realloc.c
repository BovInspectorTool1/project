// RUN: %llvmgcc %s -emit-llvm -O0 -c -o %t1.bc
// RUN: %klee --exit-on-error %t1.bc
// RUN: grep "KLEE: WARNING ONCE: Large alloc" klee-last/warnings.txt

#include <assert.h>
#include <stdlib.h>
#include <stdio.h>

int main() {
  int *p = malloc(sizeof(int)*2);
  assert(p);
  p[1] = 52;

  int *p2 = realloc(p, 1<<30);
  assert(p2[1] == 52);

  return 0;
}
