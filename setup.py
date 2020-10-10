import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="redis-sitesearch",
    version="1.0",
    author="Andrew Brookins",
    author_email="andrew.brookins@redislabs.com",
    description="Redis-powered site search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redislabs-training/redis-sitesearch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'index=sitesearch.commands.index:index',
            'search=sitesearch.commands.search:search',
            'scheduler=sitesearch.commands.scheduler:scheduler'
        ],
    }
)
