from distutils.core import setup
setup(
  name = 'scoptimize',
  packages = ['scoptimize'],
  version = '0.0.1',
  license='MIT',
  description = 'Supply Chain Optimization Package',
  author = 'Connor Makowski',
  author_email = 'conmak@mit.edu',
  url = 'https://github.com/connor-makowski/scoptimize',
  download_url = 'https://github.com/connor-makowski/scoptimize/dist/scoptimize-0.0.1.tar.gz',
  keywords = [],
  install_requires=["pamda==0.0.13", "PuLP==2.6.0", "type_enforced==0.0.4"],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],
)
