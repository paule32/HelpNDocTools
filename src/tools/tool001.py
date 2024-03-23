# ---------------------------------------------------------------------------
# File:   tool001.py - pack data
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
#
# desc: This file convert the list of "data_files" files (,dat) int gzip, and
#       base64 encoded string. A file called "collection.py" will be created.
#       The content's of the external data files will be written to .py files
# ---------------------------------------------------------------------------
from datetime import datetime
import gzip
import base64

import sys

data_files = [
    # --------------------------------------------------------------
    # input file   , variable          , type (0 = list, 1 = string)
    # --------------------------------------------------------------
    [ "data001.dat", "file_content_enc", 0 ],
    [ "data002.dat", "html_content_enc", 1 ]
]

# ---------------------------------------------------------------------------
# external python data (members):
# ---------------------------------------------------------------------------
func_code = (""
    + "\n"
    + "import gzip\n"
    + "import base64\n"
    + "\n"
    + "# " + ("-" * 78) + "\n"
    + "# convert string to list ...\n"
    + "# " + ("-" * 78) + "\n"
    + "def StrToList(string):\n"
    + (" "*4) + "li = list(string.split(\",\"))\n"
    + (" "*4) + "return li\n\n"
)

# ---------------------------------------------------------------------------
# compress the reader data ...
# ---------------------------------------------------------------------------
def compress_data(dat_file, data):
    packed_data = gzip.compress(data)
    encode_data = base64.b64encode(packed_data).decode()
    
    foo   = encode_data
    lines = [foo[i:i+80] for i in range(0, len(encode_data), 80)]
    
    new_date = datetime.now().strftime("%Y-%m-%d").encode()
    old_file = dat_file[0]
    new_file = old_file[:old_file.rfind('.')] + ".py"
    with open(new_file, "wb") as f:
        dat00 = (b""
        + b"# " + (b"-" * 78) + b"\n"
        + b"# created on:"+ new_date + b"\n"
        + b"# (c) paule32\n"
        + b"# " + (b"-" * 78) + b"\n"
        + b"global " + dat_file[1][:-4].encode() + b"\n"
        + dat_file[1][:-4].encode() + b" = (''\n")
        f.write(dat00)
        for line in lines:
            f.write(b"+ '")
            f.write(line.encode())
            f.write(b"'\n")
        f.write(b")")
        f.close()

# ---------------------------------------------------------------------------
# create a "collection" file, and array fot import modules
# ---------------------------------------------------------------------------
def create_collection(out_file):
    new_date = datetime.now().strftime("%Y-%m-%d").encode()
    with open(out_file, "wb") as f:
        f.write(b"# " + (b"-" * 78) + b"\n")
        f.write(b"# created on:"+ new_date + b"\n")
        f.write(b"# (c) 2024 by paule32\n")
        f.write(b"# all rights reserved.\n")
        f.write(b"# " + (b"-" * 78) + b"\n")
        for datafile in data_files:
            old_file = datafile[0]
            new_file = old_file[:old_file.rfind('.')]
            f.write(b"import " + new_file.encode() + b"\n")
        f.write(b"#\n")
        f.write(func_code.encode())
        for datafile in data_files:
            dat01 = (b""
                + datafile[1].encode() + b" = base64.b64decode("
                + datafile[0][:-4].encode() + b"."
                + datafile[1][:-4].encode() + b".encode())\n"
                + datafile[1].encode() + b"_data = gzip.decompress("
                + datafile[1].encode() + b").decode()\n"
                + datafile[1][:-4].encode() + b" = ")
            if datafile[2] == 0:
                dat01 = (dat01
                + b"StrToList(" + datafile[1].encode()
                + b"_data)\n")
            else:
                dat01 = dat01 + datafile[1].encode() + b"_data\n"
            f.write(dat01 + b"#\n")
        f.close()
    return

# ---------------------------------------------------------------------------
# load initial files ...
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    for datafile in data_files:
        file_path = (".\\" + datafile[0])
        with open(file_path, 'rb') as f:
            data_to_compress = f.read()
            f.close()
            compress_data(datafile, data_to_compress)
    create_collection("collection.py")
    sys.exit(0)
