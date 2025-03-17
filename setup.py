from setuptools import setup, find_packages

setup(
    name="mini-cms",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "fastapi-sso",
        "jinja2",
        "python-multipart",
    ],
    python_requires=">=3.8",
)