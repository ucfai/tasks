from setuptools import setup, find_packages

with open(".github/README.md", "r") as f:
    long_description = f.read()

setup(
    name="autobot",
    version="0.1",
    author="AI@UCF",
    author_email="bmm.ucf@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://ucfai.org/bot/",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",  # this, technically, includes MacOS/Linux
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Home Automation",  # not really for home-use, but it fits :joy:
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    # package_dir={"autobot": "src"},
    include_package_data=True,
    # namespace_packages=["autobot"],
    entry_points={"console_scripts": ["autobot = autobot.main:main"]},
    install_requires=[
        "imgkit",
        "jinja2",
        "nbformat",
        "pandas",
        "Pillow",
        "PyYAML",
        "requests",
        "nbconvert",
        "pygithub",
    ],
)
