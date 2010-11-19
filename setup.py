#Setup file for py2exe
#usage: python setup.py install
#       python setup.py py2exe

from distutils.core import setup
from glob import glob
import py2exe

appdata_files = [('res', glob(r'res/*.*')), ("Microsoft.VC90.CRT", glob(r'Microsoft.VC90.CRT/*.*'))]

setup(
    name="clark Sonic Comissioning",
    version="1.0",
    description="Initial setup of DNEM",
    author="David Tyler",
    windows=['Comissioning.py'],
    data_files = appdata_files,
    options={
        "py2exe":{
            "unbuffered": True,
            "optimize": 2
        }
    }
)