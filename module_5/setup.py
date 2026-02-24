"""
Setup configuration for GradCafe Analysis Application
"""
from setuptools import setup, find_packages

setup(
    name="gradcafe-analyzer",
    version="5.0.0",
    description="A Flask-based web application for analyzing graduate school admissions data from GradCafe",
    author="Zhendong Zhang",
    author_email="zzhan4430@jhu.edu",
    url="https://github.com/yourusername/jhu_software_concepts",
    
    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Python version requirement
    python_requires=">=3.10",
    
    # Runtime dependencies
    install_requires=[
        "Flask>=3.1.3",
        "Jinja2>=3.1.6",
        "psycopg2-binary>=2.9.9",
        "psycopg>=3.3.3",
        "python-dotenv>=1.2.1",
        "beautifulsoup4>=4.12.3",
        "lxml>=5.1.0",
    ],
    
    # Development dependencies
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pylint>=4.0.5",
            "pydeps>=3.0.2",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "gradcafe-app=app:main",
            "gradcafe-setup=setup_databases:main",
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    
    # Include additional files
    include_package_data=True,
    package_data={
        "": [
            "templates/*.html",
            "static/*.css",
            "static/*.js",
        ],
    },
)
