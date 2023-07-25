# ProcReg: A processing registry for research

Currently in development by the DH-IT portal team for the faculties of Humanities and Law, Economics, and Governance at [Utrecht University](https://uu.nl).

## Goals

While doing their work, researchers often process personal information. According to the GDPR and its Dutch implementation in the AVG, Utrecht University is responsible for recording what personal data is processed and why. Procreg aims to facilitate the registration of these data processing activities in a manner that fulfills all legal requirements while not unnecessarily adding to the bureaucratic load the researchers face.

Procreg *does not* record any actual data used in research, and is not a place to store research data. 
Procreg *does* record meta-information on data collected during research activities.

## Design

Procreg is a Django application making use of the DH-IT [Django Shared Core](https://github.com/DH-IT-Portal-Development/django-shared-core) and [Portaldev Bootstrap theme](https://github.com/DH-IT-Portal-Development/bootstrap-theme).

Procreg provides a browser-based portal in which guided questions help researchers register exactly what is necessary to fulfill their requirements under the AVG. It requires no prior knowledge on personal data collection for the end-user and therefore contains an educational component.

# Development

## Requirements

* Python 3.9+
* Pip (for installing dependencies, see requirements.txt for details)
* A SQL database (tested with SQLite and MySQL)

## Installation

* Clone this repository
* Install the dependencies using pip (it is recommended to use a virtual 
  environment!). ``pip install -r requirements.txt``
* Run all DB migrations ``python manage.py migrate``
* Edit ``procreg/settings.py`` to suit your needs.
* Create a super user using ``python manage.py createsuperuser``
* Compile the translation files using ``python manage.py compilemessages``
* You can now run a development server with ``python manage.py runserver``


## A note on dependencies
We use pip-tools to manage our dependencies (mostly to freeze the versions 
used). It's listed as a dependency, so it will be installed automatically.

``requirements.in`` lists the actual dependency and their version constraints. 
To update ``requirements.txt`` just run ``pip-compile -U``. Don't forget to test 
with the new versions!
