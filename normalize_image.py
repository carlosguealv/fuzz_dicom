from pydicom import dcmread, dcmwrite
from pydicom.uid import ExplicitVRLittleEndian
from pydicom.dataelem import DataElement
import sys

dcm = dcmread(sys.argv[1])
dcm.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian  # Convert to explicit VR

tag = (0x0028, 0x0008)  # 'Number of Frames'
if tag not in dcm:
    dcm[tag] = DataElement(tag, 'IS', 1) 

dcmwrite(sys.argv[1], dcm)

