import pylibdicom
import gdcm
from pydicom import dcmread
import difflib
import sys

def compare_files(file1, file2, file3):
    diff12 = list(difflib.unified_diff(file1, file2, lineterm=''))
    diff13 = list(difflib.unified_diff(file1, file3, lineterm=''))
    diff23 = list(difflib.unified_diff(file2, file3, lineterm=''))

    return diff12, diff13, diff23

def libdicom_print_sequence(seq, indent=0, file=None):
    if file is not None:
        for index in range(seq.count()):
            file.write(f"{' ' * indent}-- Item #{index} --\n")
            libdicom_print_dataset(seq.get(index), indent + 2, file)
    else:
        for index in range(seq.count()):
            print(f"{' ' * indent}-- Item #{index} --\n")
            libdicom_print_dataset(seq.get(index), indent + 2)

def libdicom_print_dataset(dataset, indent=0, file=None):
    if file is not None:
        for tag in dataset.tags():
            if str(tag) == "(0002,0000)" or str(tag) == "(0002,0001)":
                continue

            element = dataset.get(tag)
            
            if str(element.vr()) in ["FD", "AT", "US", "FL", "OB", "UL"]:
                continue

            file.write(f"{' ' * indent}{tag} {element.get_value()}\n")
            if element.vr_class() == pylibdicom.VRClass.SEQUENCE:
                seq = element.get_value()
                libdicom_print_sequence(seq, indent + 2, file)

    else:
        for tag in dataset.tags():
            if str(tag) == "(0002,0000)" or str(tag) == "(0002,0001)":
                continue

            element = dataset.get(tag)
            if str(element.vr()) in ["FD", "AT", "US", "FL", "OB", "UL"]:
                continue

            print(f"{' ' * indent}{tag} {element. value}\n")
            if element.vr_class() == pylibdicom.VRClass.SEQUENCE:
                seq = element.get_value()
                libdicom_print_sequence(seq, indent + 2)

def gdcm_print_sequence(seq, indent=0, file=None):
    if file is not None:
        itemNr = 1
        while itemNr <= seq.GetNumberOfItems():
            file.write(f"{' ' * indent}-- Item #{itemNr-1} --\n")
            gdcm_print_dataset(seq.GetItem(itemNr).GetNestedDataSet(), indent + 2, file)
            itemNr += 1
    else:
        itemNr = 1
        while itemNr <= seq.GetNumberOfItems():
            print(f"{' ' * indent}-- Item #{itemNr-1} --\n")
            gdcm_print_dataset(seq.GetItem(itemNr).GetNestedDataSet(), indent + 2)
            itemNr += 1

def gdcm_print_dataset(dataset, indent=0, file=None):
    if file is not None:
        it = dataset.GetDES().begin()
        while not it.equal(dataset.GetDES().end()):
            element = it.next()
            tag = element.GetTag()
            vr = str(element.GetVR())

            if element.IsEmpty():
                if vr == "SQ":
                    file.write(f"{' '*indent}{tag} <Sequence of 0 items>\n")
                continue
             
            if str(tag) == "(0002,0000)" or str(tag) == "(0002,0001)":
                continue 

            if vr == "SQ":
                value = element.GetValueAsSQ()
                file.write(f"{' '*indent}{tag} <Sequence of {value.GetNumberOfItems()} items>\n")
                gdcm_print_sequence(value, indent+2, file)
            elif vr in ["FD", "AT", "US", "FL", "OB", "OW", "OF", "UL", "UT"]:
                continue

            else:
                if "\\" in str(element.GetValue()):
                    value = str(element.GetValue()).rstrip().split('\\')
                    file.write(f"{' '*indent}{tag} {value}\n")
                    continue
                value = element.GetValue()
                file.write(f"{' '*indent}{tag} ['{str(value).rstrip()}']\n")
    else:
        it = dataset.GetDES().begin()
        while not it.equal(dataset.GetDES().end()):
            element = it.next()

            if element.IsEmpty():
                continue
            
            tag = element.GetTag()
            vr = str(element.GetVR())

            if str(tag) == "(0002,0000)" or str(tag) == "(0002,0001)":
                continue

            if vr == "CS":
                value = str(element.GetValue()).split('\\')
                print(f"{' '*indent}{tag} {value}\n")
                continue

            elif vr in ["FD", "AT", "US", "FL", "OB", "OW", "OF", "UL", "UT"]:
                continue

            if vr == "SQ":
                value = element.GetValueAsSQ()
                print(f"{' '*indent}{tag} <Sequence of {value.GetNumberOfItems()} items>\n")
                gdcm_print_sequence(seq, indent+2, file)

            else:
                value = element.GetValue()
                print(f"{' '*indent}{tag} ['{value}']\n")

def pydicom_print_sequence(seq, indent=0, file=None):
    if file is not None:
        for index, dataset in enumerate(seq):
            file.write(f"{' ' * indent}-- Item #{index} --\n")
            pydicom_print_dataset(dataset, indent + 2, file)
    else:
        for index, dataset in enumerate(seq):
            print(f"{' ' * indent}-- Item #{index} --")
            pydicom_print_dataset(dataset, indent + 2)

def pydicom_print_dataset(dataset, indent=0, file=None):
    if file is not None:
        for elem in dataset:
            if str(elem.tag) == "(0002,0000)" or str(elem.tag) == "(0002,0001)":
                continue 

            elif elem.VR == "SQ":
                file.write(f"{' ' * indent}{str(elem.tag).lower()} <Sequence of {len(elem.value)} items>\n")
                pydicom_print_sequence(elem.value, indent + 2, file)
                continue
            elif str(elem.VR) in ["FD", "AT", "US", "FL", "OB", "OW", "OF", "UL", "UT"]:
                continue

            if '[' in str(elem.value):
                if "'" in str(elem.value):
                    file.write(f"{' ' * indent}{str(elem.tag).lower()} {elem.value}\n")
                else:
                    s = str(elem.value).strip('[]')

                    items = s.split(',')

                    result = [item.strip() for item in items]
                    
                    file.write(f"{' ' * indent}{str(elem.tag).lower()} {result}\n")
                continue

            file.write(f"{' ' * indent}{str(elem.tag).lower()} ['{elem.value}']\n")
    else:
        for elem in dataset:
            if str(elem.tag) == "(0002,0000)" or str(elem.tag) == "(0002,0001)":
                continue

            if elem.VR == "CS":
                print(f"{' ' * indent}{str(elem.tag).lower()} {elem.value}\n")
                continue

            elif elem.VR == "SQ":
                print(f"{' ' * indent}{str(elem.tag).lower()} <Sequence of {len(elem.value)} items>\n")
                pydicom_print_sequence(elem.value, indent + 2)
                continue
            elif str(elem.VR) in ["FD", "AT", "US", "FL", "OB", "OW", "OF", "UL", "UT"]:
                continue

            print(f"{' ' * indent}{str(elem.tag).lower()} ['{elem.value}']\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_image.py <dicom_file>\n")
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
    meta = file.GetHeader()
    
    with open("gdcm_output.txt", "w") as output_file:
        output_file.write("===File Meta Information===\n")
        gdcm_print_dataset(meta, file=output_file)
    
        ds = file.GetDataSet()
        output_file.write("===Dataset===\n")
        gdcm_print_dataset(ds, file=output_file)
    
    # now use pydicom
    ds = dcmread(sys.argv[1])
    with open("pydicom_output.txt", "w") as output_file:
        output_file.write("===File Meta Information===\n")
        pydicom_print_dataset(ds.file_meta, file=output_file)
    
        output_file.write("===Dataset===\n")
        pydicom_print_dataset(ds, file=output_file)
    
    # Compare the outputs
    with open("libdicom_output.txt") as file_1:
        file_1_text = file_1.readlines()
    
    with open("gdcm_output.txt") as file_2:
        file_2_text = file_2.readlines()
    
    with open("pydicom_output.txt") as file_3:
        file_3_text = file_3.readlines()
    
    diff12, diff13, diff23 = compare_files(file_1_text, file_2_text, file_3_text)
    # Print differences
    print("Differences between File 1 and File 2:\n")
    print("\n".join(diff12))
    
    print("\nDifferences between File 1 and File 3:\n")
    print("\n".join(diff13))
    
    print("\nDifferences between File 2 and File 3:\n")
    print("\n".join(diff23))
