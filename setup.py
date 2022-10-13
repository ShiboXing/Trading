from setuptools import setup, Extension, find_packages

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
                "/usr/local/lib/python3.10/site-packages/numpy/core/include/",
            ],
            sources=[
                "cpp/tech/domains.cpp",
                "cpp/tech/algo.cpp",
            ],
            extra_compile_args=["-std=c++20"],
        )
    ],
)
