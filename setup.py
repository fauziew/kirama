import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Kirama", 
    version="0.1",
    author="Fauzie Wiriadisastra",
    author_email="fauziew@gmail.com",
    description="Gamelan Simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fauziew/kirama",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
