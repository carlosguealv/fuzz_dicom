from pydicom import dcmread, dcmwrite
from pydicom.uid import ExplicitVRLittleEndian
import sys

dcm = dcmread(sys.argv[1])
dcm.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian  # Convert to explicit VR
dcmwrite(sys.argv[1], dcm)

