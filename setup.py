import setuptools

with open('README.md', 'r') as fh:
  long_description = fh.read()

setuptools.setup(
  name="firestore-model",
  version="0.0.1",
  author="Future Projects",
  author_email="info@futureprojects.io",
  description="A wrapper for creating model classes using Google's Cloud Firestore schemaless database",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://gitlab.com/futureprojects/firestore-model",
  packages=setuptools.find_packages(),
  classifiers=[
      "Programming Language :: Python :: 3.7",
      "License :: OSI Approved :: GNU GPLv3",
      "Operating System :: OS Independent",
  ]
)
