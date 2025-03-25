from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="swaguard",
    version="0.1.0",
    author="Ryan",
    author_email="rise.ryan.lee@gmail.com",
    description="A library to protect Swagger/OpenAPI UI in FastAPI and Django applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/riseryan89/swaguard",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Framework :: Django",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        "fastapi>=0.70.0",
        "pydantic>=1.8.0",
        "python-multipart>=0.0.5",
        "pyyaml>=5.1",
        "bcrypt>=3.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "uvicorn>=0.15.0",
        ],
    },
)
