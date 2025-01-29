# Use the official Ubuntu image as the base image
FROM ubuntu:latest
SHELL ["/bin/bash", "-c"]

# install libdicom
RUN apt-get update && apt-get install -y \
    curl vim build-essential git cmake \
		python3 python3-pip python3-setuptools \
		python3-wheel python3-venv ninja-build afl++ meson \
		diffutils

RUN git clone https://github.com/ImagingDataCommons/libdicom.git

RUN cd libdicom && meson setup builddir --buildtype release \
	&& meson compile -C builddir && meson install -C builddir

RUN python3 -m venv dicom

RUN source /dicom/bin/activate && pip install pydicom python-gdcm

RUN git clone https://github.com/jcupitt/pylibdicom.git

COPY fuzz_dicom.py /pylibdicom/fuzz_dicom.py

COPY 0002.DCM /pylibdicom/0002.DCM
