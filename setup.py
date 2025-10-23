# Python Software Foundation License
from setuptools import setup, Extension
from Cython.Build import cythonize
import sys

# Define the Cython extension
extensions = [
    Extension(
        "odict.codict",
        ["src/odict/codict.pyx"],
        language="c",
    )
]

# Only build extensions if not in editable/development mode
# This allows the package to be installed without compilation if needed
if __name__ == "__main__":
    setup(
        ext_modules=cythonize(
            extensions,
            compiler_directives={
                'language_level': '3',
                'embedsignature': True,
            },
        ),
    )
