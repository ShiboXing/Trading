from setuptools import setup, Extension, find_packages

setup(
    name="rumble",
    version="1.0",
    packages=find_packages("."),
    ext_modules=[
        Extension(
            "rumble.tech_cpp",
            sources=["cpp/tech/domains.cpp"],
        )
    ],
)
