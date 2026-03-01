"""
Setup configuration for GradCafe Analysis Application – Module 6
"""
from setuptools import setup, find_packages

setup(
    name="gradcafe-analyzer",
    version="6.0.0",
    description="Containerised microservice version of the GradCafe analysis app",
    author="Zhendong Zhang",
    author_email="zzhan4430@jhu.edu",
    python_requires=">=3.11",
    packages=find_packages(where="src/web"),
    package_dir={"": "src/web"},
    install_requires=[
        "Flask>=3.1.3",
        "Jinja2>=3.1.6",
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.2.1",
        "pika>=1.3.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pylint>=4.0.5",
        ],
    },
)
