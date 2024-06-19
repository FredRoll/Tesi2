from setuptools import setup, find_packages

setup(
    name='survey',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_login',
        'flask_bootstrap',
        'flask_sqlalchemy',
        'flask_wtf',
    ],
)