# ---------------------------------------------------------------------------
# \file    zipfiles.py
# \author  (c) 2024 Jens Kallup - paule32
# \copy    All rights reserved
#
# \desc    Construct an application gzipped image file with the data used by
#          this application. All data will be extracted into the memory when
#          using/start.
#
# \version 0.0.1
# ---------------------------------------------------------------------------
import sys
import os
import gzip
import struct

# ---------------------------------------------------------------------------
# \brief  global variables stuff ...
# ---------------------------------------------------------------------------
global error_code; error_code = 0

# ---------------------------------------------------------------------------
# \brief  Compress given files in root "file_root", create a list of the
#         packed files. You have to give the directory (e.g. ./all) where
#         "start.pycache" file is the stub file, and the other files resides.
#
# \param  file_root    - string  # the root path
# \param  file_stub    - string  # the stub (pycache start) file
# \param  file_output  - string  # the output file
# ---------------------------------------------------------------------------
def compress_images_to_gzip(file_root, file_stub, file_output):
    try:
        image_extensions = (
            # python files ...
            'start.pyc',
            
            # image files ...
            '.jpg', '.jpeg', '.png', '.gif',
            '.bmp', '.tiff', '.webp'
        )
        image_files = []
        files_list  = []
            
        # ---------------------------------------------
        # read directories recursive into a list ...
        # ---------------------------------------------
        for root, dirs, files in os.walk(file_root):
            for file in files:
                file_name = root + "/" + file
                files_list.append(file_name)
                if file.lower().endswith(image_extensions):
                    image_files.append(os.path.join(root, file))
        
        # ---------------------------------------------
        # 1. convert list to string
        # 2. write string as gzip data
        # 3. get size of files.gz
        # 4. write file size
        # 5. write final partial file
        # ---------------------------------------------
        files_string = ", ".join(map(str, image_files))
        files_string = files_string.replace("\\", "/")
        files_string = files_string.replace("./all", ".")
        
        with gzip.open("./files.gz", "wb") as file:
            file.write(files_string.encode("utf-8"))
            file.close()
        
        # ---------------------------------------------
        # Packe die Dateigröße in einen 4-Byte-Wert
        # '>I' steht für big-endian unsigned int
        # ---------------------------------------------
        list_len = os.path.getsize("./files.gz")
        list_len_prefix = struct.pack('>I', list_len)
        
        with open("./files.gz", "rb") as file:
            list_data = file.read()
            file.close()
        
        with open("./files.gz", "wb") as file: 
            file.write(list_len_prefix)
            file.write(list_data)
            file.close()
        
        # ---------------------------------------------
        # 6. write length of compressed data
        # 7. write data
        # ---------------------------------------------
        with open("./temp.gz", 'wb') as f_out:
            for image_file in image_files:
                with open(image_file, 'rb') as f_in:
                    compressed_data = gzip.compress(f_in.read(), compresslevel=9)
                    
                    # Write the length of the compressed data followed by the data itself
                    f_out.write(len(compressed_data).to_bytes(4, byteorder='big'))
                    f_out.write(compressed_data)
            f_out.close()
        
        # ---------------------------------------------
        # 8. write final gzip file ...
        # ---------------------------------------------
        with open("./files.gz", "rb") as file:
            data_a = file.read()
            file.close()
        
        with open("./temp.gz", "rb") as file:
            data_b = file.read()
            file.close()
        
        # ---------------------------------------------
        # Packe die Dateigröße in einen 4-Byte-Wert
        # '>I' steht für big-endian unsigned int
        # ---------------------------------------------
        data_len = os.path.getsize("./temp.gz")
        data_len_prefix = struct.pack('>I', data_len)
        
        with open(file_output, "wb") as file:
            file.write(data_a)
            file.write(data_len_prefix)
            file.write(data_b)           # python + images
            #
            file.close()
        
        print(f"Compressed {len(image_files)} files into {file_output}")
        error_code = 0
    except Exception as e:
        os.remove("./files.gz")
        os.remove("./temp.gz" )
        print(e)
        error_code = 1

# ---------------------------------------------------------------------------
# \brief  Entry point of this application script.
#
# \return exitcode - int # 0 - no error; else error
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    file_root   = './all'
    file_output = './app.pyc'
    file_stub   = './stub.pyc'
    
    error_code  = 1
    
    # ---------------------------------------------
    # create the gzipped image file ...
    # ---------------------------------------------
    compress_images_to_gzip(
        file_root,
        file_stub,
        file_output)
    
    size_stub  = os.path.getsize(file_stub)
    size_image = os.path.getsize(file_output)
    
    with open(file_stub, "rb") as file:
        data_stub = file.read()
        file.close()
    
    with open("./temp.gz", "rb") as file:
        data_image = file.read()
        file.close()
    
    hex_value = format(size_image, "x")
    if len(hex_value) % 2:
        hex_value = "0" + hex_value
    
    bin_value = bytes.fromhex(hex_value)
    
    # ---------------------------------------------
    # write final image file ...
    # ---------------------------------------------
    with open(file_output, "wb") as file:
        file.write(data_stub )
        file.write(b"--payload--")
        file.write(data_image)
        file.close()

    # ---------------------------------------------
    # delete uneccassary files ...
    # ---------------------------------------------
    if os.path.exists("./files.gz"):
        os.remove("./files.gz")
    
    if os.path.exists("./temp.gz"):
        os.remove("./temp.gz" )
    
    sys.exit(error_code)
