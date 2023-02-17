# ProcReg: A processing registry for research

Currently in development by the DH-IT portal team for the faculties of Humanities and Law, Economics, and Governance at [Utrecht University](https://uu.nl).

## Goals

While doing their work, researchers often process personal information. According to the GDPR and its Dutch implementation in the AVG, Utrecht University is responsible for recording what personal data is processed and why. Procreg aims to facilitate the registration of these data processing activities in a manner that fulfills all legal requirements while not unnecessarily adding to the bureaucratic load the researchers face.

Procreg *does not* record any actual data used in research, and is not a place to store research data. 
Procreg *does* record meta-information on data collected during research activities.

## Design

Procreg is a Django application making use of the DH-IT [Django Shared Core](https://github.com/DH-IT-Portal-Development/django-shared-core) and [Portaldev Bootstrap theme](https://github.com/DH-IT-Portal-Development/bootstrap-theme).

Procreg provides a browser-based portal in which guided questions help researchers register exactly what is necessary to fulfill their requirements under the AVG. It requires no prior knowledge on personal data collection for the end-user and therefore contains an educational component.
