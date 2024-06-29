# ----------------------------------------------------------------------------
# file: downresize.py
# Author: (c) 2024 paule32 - Jens Kallup
# all rights reserved.
#
# download flags images + resize it 50 percent from the original.
# this file is part of the ovserver project.
# the playground is a csv file.
# ----------------------------------------------------------------------------
import csv
import requests
from PIL import Image
from io import BytesIO
import os

# ----------------------------------------------------------------------------
# Definiere den Pfad zur CSV-Datei und zum Speicherort der GIFs
# ----------------------------------------------------------------------------
csv_file_path    = "./flags_iso.csv"
output_file_path = "./flags_list.py"
output_directory = "./img"
result_list      = []

# ----------------------------------------------------------------------------
# Erstelle das Ausgabe-Verzeichnis, falls es nicht existiert
# ----------------------------------------------------------------------------
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# ----------------------------------------------------------------------------
# Funktion zum Herunterladen und Verkleinern eines Bildes
# ----------------------------------------------------------------------------
def download_and_resize_image(url, output_path, scale=0.5):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        new_size = (int(image.width * scale), int(image.height * scale))
        resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
        resized_image.save(output_path)
        print(f'Successfully downloaded and resized: {output_path}')
    else:
        print(f'Failed to download: {url}')

# ----------------------------------------------------------------------------
# Lies die CSV-Datei und lade die Bilder herunter
# ----------------------------------------------------------------------------
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row)
        country      = row["Country"]
        alpha_2_code = row["Alpha-2 code"]
        alpha_3_code = row["Alpha-3 code"]
        url          = row['URL']
        modified_url = f"cdn_host/{alpha_3_code}.gif"
        filename     = f"{alpha_3_code}.gif"
        #output_path  = os.path.join(output_directory, filename)
        result_list.append(f"[ \"{alpha_3_code}\", cdn_host + \"{alpha_3_code}\" + cdn_suff ]")
        #download_and_resize_image(url, output_path)
    
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write("# " + ('-' * 70) + "\n")
        output_file.write("# ATTENTION:\n")
        output_file.write("# automated generated - any change on this file will be lost\n")
        output_file.write("# (c) 2024 by paule32 - Jens Kallup <pule32.jk@gmail.com>\n")
        output_file.write("# " + ('-' * 70) + "\n")
        output_file.write("def load_flags:\n")
        output_file.write("    cdn_host = genv.__app__cdn_host + \"/observer/img/flags/\"\n")
        output_file.write("    cdn_suff = \".gif\"\n")
        output_file.write("    genv.v__app__cdn_flags = [\n")
        for entry in result_list:
            output_file.write("        " + entry + ',\n')
        output_file.write("    ]\n")
        output_file.close()

# ----------------------------------------------------------------------------
# done.
# ----------------------------------------------------------------------------
print('Download and resizing completed!')
