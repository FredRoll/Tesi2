from setuptools import setup, find_packages

setup(
    name='survey',  # nome del pacchetto
    version='0.1',
    packages=find_packages(),
    package_data={'': ['static/css/*', 'templates/*']},
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Migrate',
        'Flask-Login',
        'Flask-Bootstrap',
        'flask_wtf',
        # Aggiungi altre dipendenze necessarie qui
    ],
    entry_points={
        'console_scripts': [
            'run_survey=main:main',  # Comando per eseguire la tua app
        ],
    },
    author='Il Tuo Nome',
    author_email='tuo_email@example.com',
    description='Una breve descrizione del tuo progetto',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/tuo_username/mio_progetto',  # URL del repository se esiste
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
