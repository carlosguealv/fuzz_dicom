# Use the official Ubuntu image as the base image
FROM ubuntu:latest

# install libdicom
RUN apt-get update && apt-get install -y \
    curl vim build-essential git cmake \
		python3 python3-pip python3-setuptools \
		python3-wheel python3-venv ninja-build afl++ meson \
		diffutils

RUN git clone https://github.com/ImagingDataCommons/libdicom.git

RUN cd libdicom && meson setup builddir --buildtype release \
	&& meson compile -C builddir && meson install -C builddir

# get grassroots dicom
RUN git clone --branch release git://git.code.sf.net/p/gdcm/gdcm\
	&& mkdir gdcmbin && cd gdcmbin && cmake ../gdcm \
	&& make -j4 && make install

RUN python3 -m venv dicom

RUN source dicom/bin/activate

RUN pip install pydicom

RUN git clone git@github.com:jcupitt/pylibdicom.git

COPY fuzz_dicom.py /pylibdicom/fuzz_dicom.py

COPY 0002.DCM /pylibdicom/0002.DCM

RUN cd /pylibdicom && python3 fuzz_dicom.py
