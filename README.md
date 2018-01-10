This file is for you to describe the getmyad application. Typically
you would include information such as the information below:

Installation and Setup
======================

pip install -e.

Run Celery
==========
celery worker -Q celery,image,small-image -c 1  -n worker.%h