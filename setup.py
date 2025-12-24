from setuptools import setup, find_packages

setup(
    name="tamil-text-matcher",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "rapidfuzz>=3.0.0",
    ],
    extras_require={
        "test": ["pytest"],
    },
)
