#!/usr/bin/env python3
"""Setup configuration for ClawVault"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clawvault",
    version="0.1.0",
    author="clawito00",
    author_email="264043458+clawito00@users.noreply.github.com",
    description="🔐 Encrypted credential manager CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clawito00/clawvault",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
    ],
    entry_points={
        "console_scripts": [
            "clawvault=clawvault.cli:main",
        ],
    },
)
