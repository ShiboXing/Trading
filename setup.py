from setuptools import setup, Extension, find_packages
from os import environ

environ["CC"] = "/usr/bin/g++"

setup(
    name="rumble",
    version="1.0",
    packages=find_packages("."),
    ext_modules=[
        Extension(
            "rumble_cpp",
            include_dirs=[
                "/usr/local/Cellar/boost/1.79.0_2/include/",
                "/usr/local/include/",
            ],
            sources=[
                "cpp/tech/module.cpp",
                "cpp/tech/tech.cpp",
                "cpp/tech/domains.cpp",
            ],
            extra_compile_args=["-std=c++20"],
        )
    ],
)
