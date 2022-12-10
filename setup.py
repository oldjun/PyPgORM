#!/usr/bin/env python
from setuptools import setup, find_packages

version = '1.0.0'

with open("./README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="PyPgORM",
    version=version,
    url='https://github.com/oldjun/PyPgORM',
    author='JP Chen',
    author_email='oldjun@sina.com',
    description='Python PostgreSQL ORM',
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires=">=3.6",
    install_requires=[
        'psycopg2>=2.9.0'
    ],
    license="MIT",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Database',
    ],
)
