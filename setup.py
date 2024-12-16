from setuptools import setup, find_packages

def finding_requirements():
    """
    Returns the install_requirements to setup the habit tracking app

    Returns:
        (str): 
    """
    with open(file="requirements.txt", encoding="utf-8") as req:
        text = req.read()
        requirements = text.split("\n")
    return requirements


setup(
    name="scrape the web",
    version="1.0",
    py_modules=["main"],
    packages=find_packages(),
    install_requires=finding_requirements(),
    python_requires=">=3.12",
    entry_points="""
        [console_scripts]
        scraping=scr.main:main
    """,
)