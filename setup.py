from setuptools import setup

setup(
    name='node',
    version='0.1.0',
    packages=['node'],
    entry_points={
        'console_scripts': [
            'valis-node = node.__main__:main',
            'debug-valis-node = node.__main__:debug'
        ]
    },
    install_requires=[
        'apistar',
    ],
)
