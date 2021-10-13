from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='neocities-sync',
    version='0.1.0',
    description='Sync local directories with neocities.org sites.',
    url='https://github.com/kugland/neocities-sync',
    author='André Kugland',
    author_email='kugland@gmail.com',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
    ],
    keywords='neocities',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.8, <4',
    install_requires=['pathspec', 'colorama'],
    entry_points={
        'console_scripts': [
            'neocities-sync=neocities_sync:main',
        ],
    },
)
