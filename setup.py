from setuptools import setup, find_packages

setup(
    name='xfl',
    packages=['xfl'],
    url='https://github.com/fireflash38/xfl',
    license='CeCILL v2',
    maintainer='Ashley Straw',
    maintainer_email='as.fireflash38@gmail.com',
    description='',
    version='1.0',
    install_requires='path.py',
    scripts=['bin/create_manifest.py']
)
