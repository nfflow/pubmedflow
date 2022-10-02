import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = ["shutup",
                    "numpy",
                    "pandas",
                    "bs4",
                    "metapub",
                    "scidownl",
                    "pdfminer3",
                    "pubmed_parser"]
setuptools.setup(
    name="pubmedflow",
    version="0.0.2",
    author="Aditya Ura",
    author_email="aadityaura@gmail.com",
    description="Data Collection from pubmed made easy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT License',
    url="https://github.com/nfflow/pubmedflow",
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    include_package_data=True,
    extras_require={"qa": ["nfmodelapis"]},
)
