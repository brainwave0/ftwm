from distutils.core import setup

setup(
    # Application name:
    name="FTWM",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Ian Campos",
    author_email="iancampos.0@protonmail.com",

    # Packages
    packages=["src"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    # url="http://pypi.python.org/pypi/MyApplication_v010/",

    #
    # license="LICENSE.txt",
    # description="Useful towel-related stuff.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "xcffib",
        "opencv-python",
        "mediapipe"
    ],
)
