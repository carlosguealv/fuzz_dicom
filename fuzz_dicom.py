import pylibdicom
import gdcm
from pydicom import dcmread

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

# Open the file for writing
with open("libdicom_output.txt", "w") as output_file:
    file = pylibdicom.Filehandle.create_from_file("sm_image.dcm")
    file_meta = file.get_file_meta()
    output_file.write("===File Meta Information===\n")

    metadata = file.get_metadata()
    output_file.write("===Dataset===\n")
    libdicom_print_dataset(metadata, file=output_file)

# Now use gdcm
reader = gdcm.Reader()
reader.SetFileName("sm_image.dcm")
if (not reader.Read()):
    print("Unable to read %s" % (filename))
    quit()

file = reader.GetFile()
fileMetaInformation = file.GetHeader()

with open("gdcm_output.txt", "w") as output_file:
    output_file.write(str(fileMetaInformation))

    dataset = file.GetDataSet()
    ds_iterator = dataset.GetDES().begin()

    output_file.write("=== DICOM Metadata ===")
    printer = gdcm.Printer()
    printer.SetFile(file)
    output_file.write(str(printer))

# now use pydicom
ds = dcmread("sm_image.dcm")
with open("pydicom_output.txt", "w") as output_file:
    output_file.write(str(ds))
