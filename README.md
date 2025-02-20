# fuzz_dicom

fuzz_dicom is a Python-based project designed for fuzz testing DICOM (Digital Imaging and Communications in Medicine) files. This repository includes tools and scripts to automate and perform fuzz testing on DICOM files to uncover potential vulnerabilities and issues.

## Features

- Fuzz testing for DICOM files.
- Automation scripts for running tests.
- Integration with Docker for containerized testing environments.

## Getting Started

### Prerequisites

- Python 3.x
- Docker

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/carlosguealv/fuzz_dicom.git
    cd fuzz_dicom
    ```

2. Build the Docker container:

    ```bash
    docker build -t fuzz_dicom .
    ```

### Usage

1. Run the image in a container:

    ```bash
    docker run -it fuzz_dicom /bin/bash
    ```

2. Run the created environment and cd into the pylibdicom directory:

    ```bash
    source dicom/bin/activate && cd pylibdicom
    ```

3. Run the fuzzing script:

    ```bash
    python3 fuzz_dicom.py images/
    ```

4. Check any interesting results with the test_image.py script:

    ```bash
    python3 test_image.py images/your_image
    ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
