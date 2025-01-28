# Use the official Ubuntu image as the base image
FROM ubuntu:latest

# install libdicom
RUN apt-get update && apt-get install -y \
    curl vim build-essential git cmake \
		python3 python3-pip python3-setuptools \
		python3-wheel ninja-build afl++ meson

RUN git clone https://github.com/ImagingDataCommons/libdicom.git

RUN export CC=afl-cc && export CXX=afl-c++ && export LD=afl-ld

RUN cd libdicom && meson setup builddir --buildtype release \
	&& meson compile -C builddir && meson install -C builddir

# get grassroots dicom
RUN git clone --branch release git://git.code.sf.net/p/gdcm/gdcm && mkdir gdcmbin && cd gdcmbin

RUN cmake ../gdcm

RUN make -j4 && make install
