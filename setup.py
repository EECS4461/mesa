#!/usr/bin/env python
import re
import os
import urllib.request
import zipfile
import shutil

from setuptools import setup, find_packages
from codecs import open

requires = ["click", "cookiecutter", "networkx", "numpy", "pandas", "tornado", "tqdm"]

extras_require = {
    "dev": ["black", "coverage", "flake8", "pytest >= 4.6", "pytest-cov", "sphinx"],
    "docs": ["sphinx", "ipython"],
}

version = ""
with open("mesa/__init__.py") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

with open("README.rst", "rb", encoding="utf-8") as f:
    readme = f.read()


def merge_folders(src: str, dst: str) -> None:
    for file_name in os.listdir(src):
        file_path = os.path.join(src, file_name)
        if os.path.isdir(file_path):
            # Ensure that a folder exists, i.e. "mkdir -p"
            dest_dir = os.path.join(dst, file_name)
            os.makedirs(dest_dir, exist_ok=True)
            merge_folders(file_path, dest_dir)
            continue
        dst_file = os.path.join(dst, file_name)
        print("Creating", dst_file)
        shutil.copy(file_path, dst_file)


# Ensure Bootstrap
if not os.path.isfile("mesa/visualization/templates/js/bootstrap.js"):
    print("Downloading the Bootstrap dependency from the internet...")
    url = "https://github.com/twbs/bootstrap/releases/download/v3.3.7/bootstrap-3.3.7-dist.zip"
    zip_file = "bootstrap-dist.zip"
    urllib.request.urlretrieve(url, zip_file)
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall()
    dir = "bootstrap-3.3.7-dist"
    merge_folders(dir, "mesa/visualization/templates")
    # Cleanup
    shutil.rmtree(dir)
    os.remove(zip_file)
    print("Done")

setup(
    name="Mesa",
    version=version,
    description="Agent-based modeling (ABM) in Python 3+",
    long_description=readme,
    author="Project Mesa Team",
    author_email="projectmesa@googlegroups.com",
    url="https://github.com/projectmesa/mesa",
    packages=find_packages(),
    package_data={
        "mesa": [
            "visualization/templates/*.html",
            "visualization/templates/css/*",
            "visualization/templates/fonts/*",
            "visualization/templates/js/*",
        ],
        "cookiecutter-mesa": ["cookiecutter-mesa/*"],
    },
    include_package_data=True,
    install_requires=requires,
    extras_require=extras_require,
    keywords="agent based modeling model ABM simulation multi-agent",
    license="Apache 2.0",
    zip_safe=False,
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Life",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
    ],
    entry_points="""
        [console_scripts]
        mesa=mesa.main:cli
    """,
    python_requires=">=3.7",
)
