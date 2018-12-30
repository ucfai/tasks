from setuptools import setup, find_packages


setup(
    name="ucfai",
    packages=find_packages(),
    # package_dir={"": ""},
    include_package_data=True,
    # namespace_packages=["admin"],
    entry_points={
        "console_scripts": [
            "ucfai = ucfai.run:main"
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
    ]
)