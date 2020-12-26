import setuptools

with open('README.md', 'r') as fh:
  long_description = fh.read()

setuptools.setup(
  name="firestore_model",
  version="0.0.5",
  author="Scibeam",
  author_email="jeremy@scibeam.co",
  description="A wrapper for creating model classes using Google's Cloud Firestore schemaless database",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://gitlab.com/futureprojects/firestore-model",
  packages=setuptools.find_packages(),
  classifiers=[
      "Programming Language :: Python :: 3.7",
      "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
      "Operating System :: OS Independent",
  ]
)
