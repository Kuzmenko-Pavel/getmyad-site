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
        "Pylons==1.0.1",
        "pymongo==2.8",
        "amqplib==1.0.2",
        "pymssql==2.0.1",
        "celery==4.1.0",
        "WebOb==1.3.1",
        "slimit==0.8.1",
        "ply==3.4",
        "Pillow==3.0.0",
        "pylibmc==1.5.1",
        "urlfetch==1.0.2",
        "recaptcha-client",
        'eventlet'
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'getmyad': ['i18n/*/LC_MESSAGES/*.mo']},
    # message_extractors={'getmyad': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = getmyad.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
