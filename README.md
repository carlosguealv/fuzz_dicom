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

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Build the Docker container:

    ```bash
    docker build -t fuzz_dicom .
    ```

### Usage

1. Run the fuzz testing script:

    ```bash
    python fuzz_test.py
    ```

2. Alternatively, you can run the tests within the Docker container:

    ```bash
    docker run --rm fuzz_dicom
    ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
