import os
from setuptools import setup, Extension, find_packages
from subprocess import check_output, CalledProcessError

__version__ = "0.2.0"


class pybind_get_include:
    """Hack to get pybind incdirs AFTER it has been installed"""

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11

        return pybind11.get_include(self.user)


try:
    RATROOT = os.environ["RATROOT"]
except KeyError:
    print(
        "could not detect RATROOT. Make sure you have source 'ratpac.sh' before installing"
    )

# Get RATPAC info
rat_incdir = os.path.join(RATROOT, "include")
rat_lib = "RATEvent"
rat_libdir = os.path.join(RATROOT, "lib")

# Get root info
# Note that this will automatically add the root include dirs and library dirs
# rather than adding them directly to the call to Extension
try:
    root_args = check_output(["root-config", "--cflags", "--libs"]).decode().split()
except CalledProcessError:
    print(
        "Error calling 'root-config'. Make sure you have sourced 'thisroot.sh' before installing"
    )


extensions = [
    Extension(
        "snake",
        ["src/snake.cpp"],
        include_dirs=[
            rat_incdir, 
            pybind_get_include(),
            pybind_get_include(), 
            "src"
        ],
        libraries=[rat_lib],
        library_dirs=[rat_libdir],
        extra_compile_args=root_args,
    )
]


setup(
    name="sibyl",
    version=__version__,
    author="Morgan Askins",
    author_email="maskins@berkeley.edu",
    scripts=["scripts/sibyl"],
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=[
        "pybind11",
        "matplotlib",
        "numpy",
        "pyqt5",
        "pyqtgraph",
        "pyopengl",
        "markdown",
    ],
    install_package_data=True,
    package_data={"sibyl": ["assets/*"]},
    zip_safe=False,
    ext_package="sibyl",
    ext_modules=extensions,
)
