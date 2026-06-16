PYTHON = python3
CC = gcc

PY_DIR = py_lib
C_DIR = c_lib
GEN_DIR = gen
BUILD_DIR = gen/build

CFLAGS = -I $(C_DIR)

.PHONY: run-py gen-c build-c run-c clean

run-py:
	$(PYTHON) main.py

build-c: run-py
	mkdir -p $(BUILD_DIR)
	$(CC) $(GEN_DIR)/conv_pixel.c $(CFLAGS) -o $(BUILD_DIR)/conv_pixel
	$(CC) $(GEN_DIR)/conv_pixel_loop.c $(CFLAGS) -o $(BUILD_DIR)/conv_pixel_loop

run-c: build-c
	./$(BUILD_DIR)/conv_pixel

run-c-loop: build-c
	./$(BUILD_DIR)/conv_pixel_loop

clean:
	rm -rf $(GEN_DIR)/*.c $(BUILD_DIR)/*
