import gzip
import os
from bitarray import bitarray
import time
import brotli
import zstandard as zstd

def compress_text_file(input_file, output_file):
    with open(input_file, 'r') as f:
        original_text = f.read()

    # Compress text using gzip
    compressed_data = gzip.compress(original_text.encode())

    # Convert compressed data to bitarray
    bit_data = bitarray()
    bit_data.frombytes(compressed_data)

    # Write bit data to output file
    with open(output_file, 'wb') as f:
        bit_data.tofile(f)

    print(f"Compression complete. Original size: {len(original_text)} bytes, Compressed size: {len(compressed_data)} bytes")

def decompress_text_file(input_file, output_file):
     # Read bitarray data from input file
    with open(input_file, 'rb') as f:
        bit_data = bitarray()
        bit_data.fromfile(f)

    # Convert bitarray back to bytes
    compressed_data = bit_data.tobytes()

    # Decompress using gzip
    decompressed_data = gzip.decompress(compressed_data)

    # Write decompressed data to output file
    with open(output_file, 'wb') as f:
        f.write(decompressed_data)

    print(f"Decompression complete.")

# ------------------------- Compression using brotli / zstd -----------------------------

def compress_brotli(input_file, output_file):
    # Read original text data
    with open(input_file, 'r') as f:
        original_text = f.read()

    # Compress data using brotli
    compressed_data = brotli.compress(original_text.encode())

    # Write compressed data to output file
    with open(output_file, 'wb') as f:
        f.write(compressed_data)

    print(f"Brotli Compression complete. Original size: {len(original_text)} bytes, Compressed size: {len(compressed_data)} bytes")


def compress_zstd(input_file, output_file):
    # Read original text data
    with open(input_file, 'r') as f:
        original_text = f.read()

    # Compress data using zstd
    cctx = zstd.ZstdCompressor()
    compressed_data = cctx.compress(original_text.encode())

    # Write compressed data to output file
    with open(output_file, 'wb') as f:
        f.write(compressed_data)

    print(f"Zstd Compression complete. Original size: {len(original_text)} bytes, Compressed size: {len(compressed_data)} bytes")


# Example usage:
input_file = 'index.txt'
output_file = 'index_compressed.zst'
start_time = time.time()
compress_zstd(input_file, output_file)
end_time = time.time()
print(f"zstd compression took {end_time - start_time:.2f} seconds.")
