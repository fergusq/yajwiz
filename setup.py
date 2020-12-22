from setuptools import setup

setup(
    name="yajwiz",
    version="0.3.0",
    author="Iikka Hauhio",
    author_email="fergusq@kaivos.org",
    packages=["yajwiz"],
    description="Klingon NLP toolkit",
    long_description=open("README.rst").read(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.8',
    package_data={
        'yajwiz': ['data.json'],
    },
)
