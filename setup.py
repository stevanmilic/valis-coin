from setuptools import setup

setup(
    name='blockchain',
    version='0.1.0',
    packages=['blockchain'],
    entry_points={
        'console_scripts': [
            'blockchain = blockchain.__main__:main'
        ]
    },
)
