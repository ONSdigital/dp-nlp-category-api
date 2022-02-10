import os

from setuptools import setup
from setuptools_rust import RustExtension

setup(
    rust_extensions=[
        RustExtension(
            "ff_fasttext._ff_fasttext",
            debug=os.environ.get("BUILD_DEBUG") == "1",
        )
    ],
)
