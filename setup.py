from setuptools import setup, find_packages

setup(
    name='django-pagemenu',
    version='dev',
    description='Django app for page menus with items altering querysets or linking directly to other views.',
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    url='https://github.com/praekelt/django-pagemenu',
    packages = find_packages(),
    include_package_data=True,
)
