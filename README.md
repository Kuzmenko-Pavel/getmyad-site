This file is for you to describe the getmyad application. Typically
you would include information such as the information below:

Installation and Setup
======================

Install ``getmyad`` using easy_install::

    easy_install getmyad

Make a config file as follows::

    paster make-config getmyad config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.


Документация
============

Документация GetMyAd написана в restructured text и может быть
преобразована во множество форматов.

Для сборки документаци в виде HTML, соберите её командами::

	cd docs
	make html

После этого откройте в браузере файл ``docs/_build/html/index.html``. 