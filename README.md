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

## Setting up

It is not recommended to run or develop this application as-is. Please see the `procreg-deploy` repo (available on GitLab) for the recommended Docker deployment. The following steps create an environment that can be inserted into the Docker container for live development

### Grab the source

Simply clone it from this repo. Put it in the `./source/` directory found in the top level of `procreg-deploy`.

```bash
git clone git@github.com:DH-IT-Portal-Development/grant-tool.git grant
cd grant
git checkout acc
```

### Create virtual environment and install sources

For virtual environment management, pipenv is recommended. The Python version used is not of great importance but 3.9 is what is used in deployments, so it's best to stick with that if possible. If Python 3.9 can't be found on your system, pipenv will suggest steps to install it using Pyenv.

The following should be run in the top level of `procreg` sources, where we left off in the previous step.

```bash
pipenv shell --python=3.9
pip install requirements.txt
```

Note that this is not the same environment as the container uses. The container simply uses the root-level Python environment and site-packages inside the container. The container does not see the virtualenv, except for `src/cdh-django-core`. The development virtualenv simply exists to give your IDE something to work with.

As such, when there are inconsistencies with code inside and outside the container, the virtual env is a good place to look.

### Install Django Shared Core into the local dev environment

The development container looks for DSC within this source directory. Therefore paths and directory names below should be followed exactly.

Once again, from the top level of `procreg` sources, with your virtual environment active. If following directories are already present, you may overwrite them.

```bash
mkdir src
cd src
git clone --branch questions git@github.com:DH-IT-Portal-Development/django-shared-core.git cdh-django-core
pip install -e ./cdh-django-core
```

DSC should already have been installed when installing requirements. However, using an editable local version allows for reference and development of both projects.
