ROOTLIBS := $(shell root-config --cflags --libs)
RATLIBS := -L$(RATROOT)/lib -lRATEvent -I$(RATROOT)/include

all:
	g++ -shared -Wl,-soname,libfastrat.so $(ROOTLIBS) $(RATLIBS) -o libfastrat.so -fPIC fastrat.cpp 
clean:
	rm -f libfastrat.so
