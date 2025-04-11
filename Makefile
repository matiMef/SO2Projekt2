# This Makefile is used to build executable versions of Python scripts
# by copying them to files without the .py extension and making them executable.
# It assumes that the Python scripts have the appropriate shebang line.

# List of executables to build
EXECUTABLES = Server Client

# Default target: build all executables
all: $(EXECUTABLES)

# Pattern rule to create an executable from a .py file
%: %.py
	cp $< $@
	chmod +x $@

# Target to clean up the executables
clean:
	rm -f $(EXECUTABLES)

# Declare all and clean as phony targets
.PHONY: all clean