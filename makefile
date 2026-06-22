PYTHON = python3
CC = gcc

PY_DIR = py_lib
C_DIR = c_lib
GEN_DIR = gen
BUILD_DIR = gen/build
BUILD_M_DIR = gen/matrices

CFLAGS = -I $(C_DIR)

.PHONY: run-py gen-c build-c run-c clean

run-py:
	$(PYTHON) new_main.py

build-c:
	mkdir -p $(BUILD_DIR)
	mkdir -p $(BUILD_M_DIR)
	$(CC) $(GEN_DIR)/conv_pixel.c $(CFLAGS) -o $(BUILD_DIR)/conv_pixel
	$(CC) $(GEN_DIR)/conv_pixel_loop.c $(CFLAGS) -o $(BUILD_DIR)/conv_pixel_loop

run-c: build-c
	./$(BUILD_DIR)/conv_pixel

run-c-loop: build-c
	./$(BUILD_DIR)/conv_pixel_loop

run-all-c: build-c
	./$(BUILD_DIR)/conv_pixel
	./$(BUILD_DIR)/conv_pixel_loop

clean:
	rm -rf $(GEN_DIR)/*.c $(BUILD_DIR)/* $(BUILD_M_DIR)/*
