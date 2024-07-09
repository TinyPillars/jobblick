import os
from setuptools import setup, find_packages

# Function to read the requirements from the requirements.txt file
def read_requirements():
    with open('requirements.txt') as req_file:
        return req_file.read().splitlines()

# Function to read the README.md file for the long description
def read_readme():
    with open('README.md') as readme_file:
        return readme_file.read()

# Setup configuration
setup(
    name='jobblick',
    version='0.1.0',
    description='A cool platform where you can review companies, employers and talk to people in your industry',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='TinyPillars',
    author_email='tinypillars@contact.com',  # Replace with the actual author's email
    url='https://github.com/TinyPillars/jobblick',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: Creative Commons NonCommercial (CC BY-NC) License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'jobblick=jobblick.cli:main',  # Make sure this points to the correct CLI entry point
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/TinyPillars/jobblick/issues',
        'Source': 'https://github.com/TinyPillars/jobblick',
    },
    keywords='job management, job tracking, job scheduler',
)

# Note: Ensure you have a README.md file and a requirements.txt file in your project root directory.
# The jobblick.cli:main should be the entry point of your command-line interface.
