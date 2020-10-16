from setuptools import setup

setup(
    name='STI Messenger',
    version='0.1.0',
    packages=['messenger'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'pymysql',
    ],
    extras_require={
        'staging': [
            'uwsgi',
        ]
    }
)
