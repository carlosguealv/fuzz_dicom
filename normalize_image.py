from pydicom import dcmread, dcmwrite
from pydicom.uid import ExplicitVRLittleEndian
import sys

dcm = dcmread(sys.argv[1])
dcm.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian  # Convert to explicit VR

# Re-add missing required tags for pylibdicom
required_tags = [(0x0028, 0x0008)]  # List of required tags
for tag in required_tags:
    if tag not in dcm:
        dcm[tag] = "1"  # Assign a reasonable default

dcmwrite(sys.argv[1], dcm)

