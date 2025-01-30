import pylibdicom
import gdcm
from pydicom import dcmread
import difflib
import sys

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
    output_file.write(str(fileMetaInformation))
    output_file.write("===File Meta Information===\n")

    dataset = file.GetDataSet()
    output_file.write("===Dataset===\n")
    output_file.write(str(dataset))

# now use pydicom
ds = dcmread(sys.argv[1])
with open("pydicom_output.txt", "w") as output_file:
    output_file.write(str(ds))

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

diff12, diff13, diff23 = compare_files(file_1_text, file_2_lines, file_3_lines)

# Print differences
print("Differences between File 1 and File 2:")
print("\n".join(diff12))

print("\nDifferences between File 1 and File 3:")
print("\n".join(diff13))

print("\nDifferences between File 2 and File 3:")
print("\n".join(diff23))
