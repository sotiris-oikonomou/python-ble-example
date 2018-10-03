import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gatt_example",
    version="0.0.1",
    author="Sotiris Oikonomou",
    author_email="contact@sotirisoikonomou.com",
    description="A BLE gatt peripheral (server) example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sotiris-oikonomou/python-bluez-peripheral-example",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3.0",
        "Operating System :: OS Independent",
    ],
)
