from setuptools import setup, find_packages

setup(
    name='openinterests',
    version='R0',
    description="Data store for European interests data.",
    long_description='',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        ],
    keywords='europe networks networks journalism ddj',
    author='Friedrich Lindenberg',
    author_email='friedrich.lindenberg@okfn.org',
    url='http://pudo.org',
    license='AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[],
    tests_require=[],
    entry_points=\
    """ """,
)
