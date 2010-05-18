from setuptools import setup, find_packages

setup(
    name='radio2000',
    version='dev',
    description='Radio2000 Django project with site specific customizations.',
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    url='https://github.com/praekelt/radio2000',
    packages = find_packages(),
    install_requires = [
        #'django-generate>=0.0.1',
        'django-generate==dev',
    ],
    include_package_data=True,
)
