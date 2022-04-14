from distutils.core import setup
setup(
  name = 'scnd',
  packages = ['scnd'],
  version = '0.0.1',
  license='MIT',
  description = 'SCND',
  author = 'Connor Makowski',
  author_email = 'connor.m.makowski@gmail.com',
  url = 'https://github.com/connor-makowski/scnd',
  download_url = 'https://github.com/connor-makowski/pamda/dist/scnd-0.0.1.tar.gz',
  keywords = [],
  install_requires=["pamda==0.0.13", "PuLP==2.6.0"],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],
)
