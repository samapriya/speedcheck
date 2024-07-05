import os

from setuptools import find_packages, setup


def readme():
    with open("README.md", encoding="utf-8") as f:
        return f.read()

setup(
    name="speedcheck",
    version="0.0.3",
    python_requires=">=3.9",
    packages=find_packages(),
    url="https://github.com/samapriya/speedcheck",
    install_requires=[
        "deepdiff>=7.0.1",
        "playwright>=1.44.0",
        "requests>=2.32.3",
        "speedtest-cli>=2.1.3",
        "websockets>=12.0",
    ],
    license="Apache 2.0",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    author="Samapriya Roy",
    author_email="samapriya.roy@gmail.com",
    description="Simple CLI for running internet speed tests",
    entry_points={"console_scripts": ["speedcheck=speedcheck.speedcheck:main"]},
)
