try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='getmyad',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='',
    install_requires=[
        "Pylons>=1.0.2",
        "pymongo==3.6.0",
        "amqplib==1.0.2",
        "pymssql==2.0.1",
        "celery==4.1.0",
        "WebOb==1.7.4",
        "slimit==0.8.1",
        "ply==3.4",
        "Pillow==3.0.0",
        "pylibmc==1.5.2",
        "urlfetch==1.0.2",
        "recaptcha-client",
        "eventlet==0.21.0"

    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'getmyad': ['i18n/*/LC_MESSAGES/*.mo']},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = getmyad.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
