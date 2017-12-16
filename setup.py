from setuptools import setup, find_packages

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name="Usor",
    version="1.0",
    description="[REST API] User Management System in vanilla Flask," 
                "Marshmallow and mongoengine with Token-Based Authentication",
    author="Drayuk",
    author_email="ekentiako@gmail.com",
    license="MIT License",
    url="https://github.com/drayuk/usor",
    py_modules=["usor"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=REQUIREMENTS,
    long_description=__doc__,
    classifiers=[
        "Development Status :: 1.0 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers, Users",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Dynamic Content :: Application",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    test_suite="tests",
    tests_require=[
        "py",
        "pytest",
        "pytest-cov",
        "cov-core",
        "coverage",
        "tox"
    ],
    setup_requires=[
        "pytest-runner",
    ],
)
