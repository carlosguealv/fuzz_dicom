FROM ubuntu:22.04

WORKDIR /root

# install libdicom
RUN apt update \
 && apt install -y software-properties-common curl vim build-essential git cmake python3.11-dev python3.11-venv ninja-build afl++ meson diffutils pkg-config diffsutils hexedit

RUN git clone https://github.com/ImagingDataCommons/libdicom.git

RUN cd libdicom \
 && meson setup builddir --buildtype release \
 && meson compile -C builddir \
 && meson install -C builddir \
 && ldconfig

RUN python3.11 -m venv dicom

RUN . dicom/bin/activate \
 && pip install pydicom python-gdcm cffi atheris

RUN git clone https://github.com/jcupitt/pylibdicom.git

COPY fuzz_dicom.py pylibdicom/fuzz_dicom.py

COPY test_image.py pylibdicom/test_image.py

COPY minimizer.py pylibdicom/minimizer.py

COPY images/ pylibdicom/images/

COPY test_cases/* /tmp/

RUN echo '. /root/dicom/bin/activate' >> /root/.bashrc
