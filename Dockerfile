# Use the official Ubuntu image as the base image
FROM ubuntu:latest
SHELL ["/bin/bash", "-c"]

# install libdicom
RUN apt-get update && apt-get install -y software-properties-common

RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y \
    curl vim build-essential git cmake \
		python3.11 python3.11-dev python3.11-venv \
		ninja-build afl++ meson \
		diffutils

RUN git clone https://github.com/ImagingDataCommons/libdicom.git

RUN cd libdicom && meson setup builddir --buildtype release \
	&& meson compile -C builddir && meson install -C builddir && ldconfig

RUN python3.11 -m venv dicom

RUN source /dicom/bin/activate && pip install pydicom python-gdcm cffi atheris

RUN git clone https://github.com/jcupitt/pylibdicom.git

COPY fuzz_dicom.py /pylibdicom/fuzz_dicom.py

COPY test_image.py /pylibdicom/test_image.py

COPY images/ /pylibdicom/images/
