from distutils.core import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'scoptimize',
  packages = ['scoptimize'],
  version = '0.0.8',
  license='MIT',
  description = 'Supply Chain Optimization Package',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Connor Makowski',
  author_email = 'conmak@mit.edu',
  url = 'https://github.com/connor-makowski/scoptimize',
  download_url = 'https://github.com/connor-makowski/scoptimize/dist/scoptimize-0.0.8.tar.gz',
  keywords = [],
  install_requires=["pulp @ git+https://github.com/connor-makowski/pulp.git@c2b350ce8fec165a21f3096dfde95202ac620048", "type_enforced>=0.0.14"],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],
)
