from setuptools import find_packages, setup

package_name = "square_file_store"

setup(
    name=package_name,
    version="1.0.0",
    packages=find_packages(),
    package_data={
        package_name: ["data/*", "pydantic_models/*"],
    },
    install_requires=[
        "uvicorn>=0.24.0.post1",
        "fastapi>=0.104.1",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.3",
        "pytest>=8.0.0",
        "square_logger>=1.0.0",
        "square_database_helper>=0.0.3",
        "square_commons>=0.0.3",
        "square_database_structure>=0.0.6",
    ],
    author="thePmSquare",
    author_email="thepmsquare@gmail.com",
    description="file storage layer for my personal server.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url=f"https://github.com/thepmsquare/{package_name}",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
