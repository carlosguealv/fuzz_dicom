import pylibdicom
import gdcm
from pydicom import dcmread
import difflib
import sys
import re

def parse_libdicom_output(filepath):
    """Parses libdicom output and extracts standard metadata."""
    metadata = {}
    with open(filepath, "r") as f:
        lines = f.readlines()

    for line in lines:
        match = re.match(r"\((\w{4},\w{4})\)\s+\S+\s+\d+\s+(.+)", line)
        if match:
            tag, value = match.groups()
            metadata[tag] = value.strip()

    return metadata

def parse_gdcm_output(filepath):
    """Parses GDCM output and extracts standard metadata."""
    metadata = {}
    with open(filepath, "r") as f:
        lines = f.readlines()

    for line in lines:
        match = re.match(r"\((\w{4},\w{4})\)\s+(\S+)", line)
        if match:
            tag, value = match.groups()
            metadata[tag] = value.strip()

    return metadata

def parse_pydicom_output(filepath):
    """Parses pydicom output and extracts standard metadata."""
    metadata = {}
    with open(filepath, "r") as f:
        lines = f.readlines()

    for line in lines:
        match = re.match(r"(\(\w{4},\w{4}\))\:\s+.*?=\s*(.*)", line)
        if match:
            tag, value = match.groups()
            metadata[tag] = value.strip()

    return metadata

def compare_metadata(libdicom_data, gdcm_data, pydicom_data):
    """Compares metadata extracted from different libraries and highlights differences."""
    all_keys = set(libdicom_data.keys()) and set(gdcm_data.keys()) and set(pydicom_data.keys())
    
    differences = {}
    
    for key in sorted(all_keys):
        libdicom_value = libdicom_data.get(key, "")
        gdcm_value = gdcm_data.get(key, "")
        pydicom_value = pydicom_data.get(key, "")
        
        if libdicom_value != gdcm_value or libdicom_value != pydicom_value:
            differences[key] = (libdicom_value, gdcm_value, pydicom_value)

    return differences

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
    for elem in ds:
        output_file.write(f"{elem.tag}: {elem.name} = {elem.value}\n")

# Compare the outputs
libdicom_data = parse_libdicom_output("libdicom_output.txt")
gdcm_data = parse_gdcm_output("gdcm_output.txt")
pydicom_data = parse_pydicom_output("pydicom_output.txt")
print(pydicom_data)

differences = compare_metadata(libdicom_data, gdcm_data, pydicom_data)
print("Differences:")
print(differences)
