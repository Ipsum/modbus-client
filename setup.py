#Setup file for py2exe
#usage: python setup.py install
#       python -OO setup.py py2exe

from distutils.core import setup
from glob import glob
import py2exe

appdata_files = [('res', glob(r'res/*.*')), ("Microsoft.VC90.CRT", glob(r'Microsoft.VC90.CRT/*.*'))]

setup(
    name="clark Sonic Comissioning",
    version="1.0",
    description="Initial setup of DNEM",
    author="David Tyler",
    windows=[
        {
            "script": "Comissioning.py",
            "icon_resources": [(1, "res/favicon.ico")]
        }
    ],
    data_files = appdata_files,
    options={
        "py2exe":{
            "ascii": True,
            "excludes": ["_ssl","doctest","pdb","unittest","difflib","inspect","pickle","calendar","optparse","locale"],
            "compressed": True,
            "unbuffered": True,
            "optimize": 2,
            "bundle_files": 3,
        }
    }
)