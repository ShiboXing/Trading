from setuptools import setup, Extension, find_packages

setup(
    name="rumble",
    version="1.0",
    packages=find_packages("."),
    ext_modules=[
        Extension(
            "rumble_cpp",
            sources=["cpp/tech/domains.cpp"],
            extra_compile_args=["-std=c++20"],
        )
    ],
)
