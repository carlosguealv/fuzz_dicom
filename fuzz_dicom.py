import pylibdicom
import gdcm
from pydicom import dcmread
import difflib
import sys
import re

class FileParser:
    '''
    A class that helps parse the metadata for further fuzzing
    '''
    def __init__(self, file_path: str):
        self.values = {}
        self.file_path = file_path

    def parse(self):
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    match = re.search(r'\((\d+),\s*(\d+)\)\s*(\d+)', line)
                    if match:
                        key = (int(match.group(1)), int(match.group(2)))
                        value = int(match.group(3))
                        self.values[key] = value
        except FileNotFoundError:
            print(f"The file {self.file_path} was not found.")
    def get_values(self):
        return self.values


def libdicom_print_sequence(seq, indent=0, file=None):
    if file is not None:
        for index in range(seq.count()):
            file.write(f"{' ' * indent}-- Item #{index} --\n")
            libdicom_print_dataset(seq.get(index), indent + 2, file)
    else:
        for index in range(seq.count()):
            print(f"{' ' * indent}-- Item #{index} --")
            libdicom_print_dataset(seq.get(index), indent + 2)

def libdicom_print_dataset(dataset, indent=0, file=None):
    if file is not None:
        for tag in dataset.tags():
            element = dataset.get(tag)
            file.write(f"{' ' * indent}{element}\n")
            if element.vr_class() == pylibdicom.VRClass.SEQUENCE:
                seq = element.get_value()
                libdicom_print_sequence(seq, indent + 2, file)
    else:
        for tag in dataset.tags():
            element = dataset.get(tag)
            print(f"{' ' * indent}{element}")
            if element.vr_class() == pylibdicom.VRClass.SEQUENCE:
                seq = element.get_value()
                libdicom_print_sequence(seq, indent + 2)

if len(sys.argv) != 2:
    print("Usage: python fuzz_dicom.py <dicom_file>")
    quit()

# Open the file for writing
with open("libdicom_output.txt", "w") as output_file:
    file = pylibdicom.Filehandle.create_from_file(sys.argv[1])
    file_meta = file.get_file_meta()
    output_file.write("===File Meta Information===\n")
    libdicom_print_dataset(file_meta, file=output_file)

    metadata = file.get_metadata()
    output_file.write("===Dataset===\n")
    libdicom_print_dataset(metadata, file=output_file)

# Now use gdcm
reader = gdcm.Reader()
reader.SetFileName(sys.argv[1])
if (not reader.Read()):
    print("Unable to read %s" % sys.argv[1])
    quit()

file = reader.GetFile()
fileMetaInformation = file.GetHeader()

with open("gdcm_output.txt", "w") as output_file:
    output_file.write("===File Meta Information===\n")
    output_file.write(str(fileMetaInformation))

    dataset = file.GetDataSet()
    output_file.write("===Dataset===\n")
    output_file.write(str(dataset))

# now use pydicom
ds = dcmread(sys.argv[1])
with open("pydicom_output.txt", "w") as output_file:
    output_file.write(str(ds))

# Parse the files
file_parser = FileParser("libdicom_output.txt")
file_parser.parse()
libdicom_values = file_parser.get_values()

file_parser = FileParser("gdcm_output.txt")
file_parser.parse()
gdcm_values = file_parser.get_values()

file_parser = FileParser("pydicom_output.txt")
file_parser.parse()
pydicom_values = file_parser.get_values()

# Rewrite the files with the values
with open("libdicom_output.txt", "w") as file:
    for key, value in libdicom_values.items():
        file.write(f"{key} {value}\n")

with open("gdcm_output.txt", "w") as file:
    for key, value in gdcm_values.items():
        file.write(f"{key} {value}\n")

with open("pydicom_output.txt", "w") as file:
    for key, value in pydicom_values.items():
        file.write(f"{key} {value}\n")

# Compare the outputs
with open("libdicom_output.txt") as file_1:
    file_1_text = file_1.readlines()

with open("gdcm_output.txt") as file_2:
    file_2_text = file_2.readlines()

with open("pydicom_output.txt") as file_3:
    file_3_text = file_3.readlines()

def compare_files(file1, file2, file3):
    diff12 = list(difflib.unified_diff(file1, file2, lineterm=''))
    diff13 = list(difflib.unified_diff(file1, file3, lineterm=''))
    diff23 = list(difflib.unified_diff(file2, file3, lineterm=''))
    
    return diff12, diff13, diff23

diff12, diff13, diff23 = compare_files(file_1_text, file_2_text, file_3_text)

# Print differences
print("Differences between File 1 and File 2:")
print("\n".join(diff12))

print("\nDifferences between File 1 and File 3:")
print("\n".join(diff13))

print("\nDifferences between File 2 and File 3:")
print("\n".join(diff23))
