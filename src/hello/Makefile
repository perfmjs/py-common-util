all: foo.so
foo.o: foo.cc
	gcc -fPIC -Wall -g -c foo.cc
foo.so: foo.o
	gcc -shared -fPIC -o foo.so foo.o
	cp foo.so ../../py_common_util/hello/python/foo.so
clean:
	rm -f *.o *.so
	rm ../../py_common_util/hello/python/foo.so
