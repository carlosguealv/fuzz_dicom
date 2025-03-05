import atheris
import tempfile
import pylibdicom
import gdcm
from pydicom import dcmread
import difflib
import sys
import os

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
            elif vr in ["FD", "AT", "US", "FL", "OB", "UL"]:
                continue

            else:
                if "\\" in str(element.GetValue()):
                    value = str(element.GetValue()).rstrip().split('\\')
                    output_file.write(f"{' '*indent}{tag} {value}\n")
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

            elif vr in ["FD", "AT", "US", "FL", "OB", "UL"]:
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
            elif str(elem.VR) in ["FD", "AT", "US", "FL", "OB", "UL"]:
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
            elif str(elem.VR) in ["FD", "AT", "US", "FL", "OB", "UL"]:
                continue

            print(f"{' ' * indent}{str(elem.tag).lower()} ['{elem.value}']\n")

# --- Differential fuzzing entry point ---
def differential_fuzz(data):
    import io
    # Write fuzz data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        filename = tmp.name

    # Ensure the file has a .dcm extension
    new_filename = filename + ".dcm"
    os.rename(filename, new_filename)
    filename = new_filename  # Update filename reference

    # Create StringIO objects to capture outputs from each library.
    libdicom_out = io.StringIO()
    gdcm_out = io.StringIO()
    pydicom_out = io.StringIO()

    # --- Process with pylibdicom ---
    try:
        file = pylibdicom.Filehandle.create_from_file(filename)
        file_meta = file.get_file_meta()
        libdicom_out.write("===File Meta Information===\n")
        libdicom_print_dataset(file_meta, file=libdicom_out)
        metadata = file.get_metadata()
        libdicom_out.write("===Dataset===\n")
        libdicom_print_dataset(metadata, file=libdicom_out)
    except Exception as e:
        libdicom_out.write("Error in pylibdicom: " + str(e))

    # --- Process with gdcm ---
    try:
        reader = gdcm.Reader()
        reader.SetFileName(filename)
        if not reader.Read():
            gdcm_out.write("Unable to read file with gdcm")
        else:
            file = reader.GetFile()
            meta = file.GetHeader()
            gdcm_out.write("===File Meta Information===\n")
            gdcm_print_dataset(meta, file=gdcm_out)
            ds = file.GetDataSet()
            gdcm_out.write("===Dataset===\n")
            gdcm_print_dataset(ds, file=gdcm_out)
    except Exception as e:
        gdcm_out.write("Error in gdcm: " + str(e))

    # --- Process with pydicom ---
    try:
        ds = dcmread(filename)
        pydicom_out.write("===File Meta Information===\n")
        pydicom_print_dataset(ds.file_meta, file=pydicom_out)
        pydicom_out.write("===Dataset===\n")
        pydicom_print_dataset(ds, file=pydicom_out)
    except Exception as e:
        pydicom_out.write("Error in pydicom: " + str(e))

    # Optionally compare outputs (this diff can be used to flag inconsistencies).
    libdicom_text = libdicom_out.getvalue().splitlines()
    gdcm_text = gdcm_out.getvalue().splitlines()
    pydicom_text = pydicom_out.getvalue().splitlines()

    diff12, diff13, diff23 = compare_files(libdicom_text, gdcm_text, pydicom_text)
    # For demonstration, we simply compute the diffs.
    # You might want to log or analyze these differences further.
    return

def TestOneInput(data):
    differential_fuzz(data)

def main():
    atheris.instrument_all()
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
