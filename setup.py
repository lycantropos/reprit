from pathlib import Path

from setuptools import (find_packages,
                        setup)

import reprit

project_base_url = 'https://github.com/lycantropos/reprit/'

setup_requires = [
    'pytest-runner>=4.2',
]
tests_require = [
    'pytest>=3.8.1',
    'pytest-cov>=2.6.0',
    'hypothesis>=3.73.1',
]

setup(name=reprit.__name__,
      packages=find_packages(exclude=('tests', 'tests.*')),
      version=reprit.__version__,
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
      ],
      license='MIT License',
      description=reprit.__doc__,
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5.3',
      setup_requires=setup_requires,
      tests_require=tests_require)
