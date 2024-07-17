import os
import sys
import gzip
from io import BytesIO
from PIL import Image

with open("./app.pyc", 'rb') as file:
    data_byte = file.read()
    file.close()

pos         = 0
bytes_pos   = 0
image_index = 4

while pos < len(data_byte):
    c = data_byte[pos]
    if c == ord('-'):
        pos += 1
        c = data_byte[pos]
        if c == ord('-'):
            pos += 1
            c = data_byte[pos]
            if c == ord('p'):
                pos += 1
                c = data_byte[pos]
                if c == ord('a'):
                    pos += 1
                    c = data_byte[pos]
                    if c == ord('y'):
                        pos += 1
                        c = data_byte[pos]
                        if c == ord('l'):
                            pos += 1
                            c = data_byte[pos]
                            if c == ord('o'):
                                pos += 1
                                c = data_byte[pos]
                                if c == ord('a'):
                                    pos += 1
                                    c = data_byte[pos]
                                    if c == ord('d'):
                                        pos += 1
                                        c = data_byte[pos]
                                        if c == ord('-'):
                                            pos += 1
                                            c = data_byte[pos]
                                            if c == ord('-'):
                                                bytes_pos = pos
                                                print("found")
                                                break;
                                            else:
                                                pos += 1
                                                continue
                                        else:
                                            pos += 1
                                            continue
                                    else:
                                        pos += 1
                                        continue
                                else:
                                    pos += 1
                                    continue
                            else:
                                pos += 1
                                continue
                        else:
                            pos += 1
                            continue
                    else:
                        pos += 1
                        continue
                else:
                    pos += 1
                    continue
            else:
                pos += 1
                continue
        else:
            pos += 1
            continue
    else:
        pos += 1
        continue

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
            byte_stream = BytesIO(compressed_data)
            with gzip.GzipFile(fileobj=byte_stream) as gz_file:
                image_data = gz_file.read()
                image = Image.open(BytesIO(image_data))
                file.close()
                image.show()
                sys.exit(0)
                #return image
        index += 1
    file.close()

print("something went wrong.")
sys.exit(0)
