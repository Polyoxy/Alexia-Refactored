from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read the contents of your requirements file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='alexia',
    version='1.0.0',
    author='Aurora Developer Operations',
    description='A professional, high-performance terminal interface for Ollama.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        alexia=alexia.ui.__main__:main
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Terminals",
    ],
    python_requires='>=3.8',
)
