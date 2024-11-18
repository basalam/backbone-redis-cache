import setuptools
setuptools.setup(
    name="basalam.backbone-redis-cache",
    author="Mojtabaa Habibain",
    author_email="mojtabaa.hn@gmail.com",
    description="Python Utilities & Basalam Micro-Services SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    setuptools_git_versioning={"enabled": True},
    setup_requires=["setuptools-git-versioning"],
)
