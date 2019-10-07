#include "foo.h"

int bar() {
    return 42;
}

extern "C" // required when using C++ compiler
long long calc_mysum(int n, int* array) {
    // return type is 64 bit integer
    long long res = 0;
    for (int i = 0; i < n; ++i) {
        res += array[i];
    }
    return res;
}