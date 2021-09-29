import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()


with open("requirements.txt", "r") as reqs:
    requirements = reqs.read()


setuptools.setup(
    name="redis-sitesearch",
    version="1.0",
    author="Andrew Brookins",
    author_email="andrew.brookins@redislabs.com",
    description="Redis-powered website search by Redis Labs.",
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
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'index=sitesearch.commands.index:index',
            'search=sitesearch.commands.search:search',
            'drop_index=sitesearch.commands.drop_index:drop_index',
            'clear_old_indexes=sitesearch.commands.clear_indexes:clear_indexes',
            'build_images=sitesearch.commands.deploy:build_images',
            'deploy_app=sitesearch.commands.deploy:deploy_app',
            'deploy_worker=sitesearch.commands.deploy:deploy_worker'
        ],
    }
)
