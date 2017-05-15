from setuptools import setup

dependency_links = []

requirements = [
    'Django==1.10.5',
    'django-redis==4.7.0',
    'psycopg2==2.6.2',
    'colorlog==2.10.0',

    'pyquery==1.2.17',
    'requests==2.13.0',

    'gevent==1.2.1',
    'eventlet==0.20.1',
    'netifaces==0.10.5',

    'celery==4.0.2',
    'gunicorn==19.6.0',

    'raven==6.0.0',
    'minio==2.2.1',
    'youtube-dl',
]

tests_require = [
    #  'pytest-django==3.0.0',
    #  'pyflakes==1.1.0',
    #  'pep8==1.7.0',
    #  'pytest==3.0.3',
    #  'pytest-flake8==0.7',
    #  'pytest-pep8==1.0.6',
    #  'pytest-mock==1.2',
]

ci_require = [
    #  'coverage==4.2',
]

extras_require = {
    'dev': [
        #  'django-debug-toolbar==1.6'
    ] + tests_require,
    'test': tests_require,
    'ci': ci_require + tests_require,
}


def main():
    setup(
        name="scraper",
        version='0.0.1',
        install_requires=requirements,
        extras_require=extras_require,
        dependency_links=dependency_links,
        packages=[],
        package_dir={},
    )


if __name__ == "__main__":
    main()
