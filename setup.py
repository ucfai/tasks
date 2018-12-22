import setuptools

with open(".github/README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="ucfai-admin",
    version="0.1",
    author="AI@UCF",
    author_email="admins@ai.cs.ucf.edu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://ai.cs.ucf.edu/admin/",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX", # this, technically, includes MacOS/Linux
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Home Automation", # not really for home-use, but it fits :joy:
        "Topic :: Utilities",
    ]
)