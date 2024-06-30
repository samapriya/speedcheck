# SpeedCheck

![PyPI - Version](https://img.shields.io/pypi/v/speedcheck)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI speedcheck](https://github.com/samapriya/speedcheck/actions/workflows/CI.yml/badge.svg)](https://github.com/samapriya/speedcheck/actions/workflows/CI.yml)

**SpeedCheck** is a simple command-line interface (CLI) tool designed to help users measure their internet speed using various popular speed test providers. Whether you want to check the performance of your connection through Cloudflare, Fast.com, Ookla, or M-Lab, SpeedCheck provides a unified and straightforward way to run these tests from the command line. This tool consolidates multiple speed test services into one easy-to-use package, allowing users to quickly and efficiently assess their internet connection's download and upload speeds, latency, and overall performance.


## Features

- Run speed tests from multiple providers:
  - Cloudflare
  - Fast.com
  - Ookla
  - M-Lab
  - Speed Smart
  - Open Speed Test
- Check and compare the installed version of SpeedCheck with the latest version available on PyPI.
- Get information about the speed tests supported by SpeedCheck.
- SpeedCheck also notifies you if a newer version of the package is available on PyPI.

## Installation

To install SpeedCheck, use pip:

```
pip install speedcheck
```

## Setup
We recommend using a virtual environment to manage dependencies. Once your virtual environment is set up, make sure to run the following command to ensure that the necessary browsers are downloaded

```
playwright install
```

The rest of the setup is handled through setup.py. This project is in its early stages, so your feedback and contributions are highly appreciated.

## Usage

**Getting Information**: To get information about the supported speed tests, use the info command:

```
speedcheck info
```

**Running Speed Tests**: To run a speed test, use the run command followed by the --type argument to specify the speed test provider.

```
speedcheck run --type [provider]
```

Replace **provider** with one of the following options:

* cloudflare
* fast
* ookla
* mlab
* speedsmart
* openspeedtest

Example:

```
speedcheck run --type cloudflare
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub. We encourage pull requests to add additional testers to the SpeedCheck tool.

## Contact
For any questions or suggestions, feel free to open an issue on the GitHub repository.

## Changelog

#### v0.0.2
- added speedsmart and openspeedtest
- increased project maturity to beta
- added readme docs
