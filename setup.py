from setuptools import setup

setup(
    name="cm-project",
    version="0.1",
    description="Mythological Invasion",
    py_modules=["main"],
    package_dir={"":"src"},
    install_requires=[
        "fastapi[full]",
        "redis-om"
    ]
)
