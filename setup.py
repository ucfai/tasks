from setuptools import setup, find_packages


setup(
    name="autobot",
    packages=find_packages(),
    # package_dir={"autobot": "src"},
    include_package_data=True,
    # namespace_packages=["autobot"],
    entry_points={
        "console_scripts": [
            "autobot = autobot.main:main"
        ]
    },
    install_requires=[
        'imgkit',
        'jinja2',
        'nbformat',
        'pandas',
        'Pillow',
        'PyYAML',
        'requests',
        'nbconvert',
        'pygithub',
    ]
)
