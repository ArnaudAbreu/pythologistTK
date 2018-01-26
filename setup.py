from setuptools import setup, find_packages

setup(name='pythologistTK',
      version='0.1',
      description='Tkinter-based GUI assistant for whole slide images visualization and annotation',
      author='Arnaud Abreu',
      author_email='arnaud.abreu.p@gmail.com',
      packages=find_packages(),
      zip_safe=False,
      install_requires=['numpy'],
      include_package_data=True)
