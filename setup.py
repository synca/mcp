#!/usr/bin/env python3

"""Setup script for snake.mcp.server."""

from setuptools import setup, find_namespace_packages


setup(
    name="snake.mcp.server",
    version=open("VERSION").read().strip(),
    author="Python Team",
    author_email="python@example.com",
    description="Python tools for MCP server",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    url="https://github.com/example/snake.mcp.server",
    packages=find_namespace_packages(include=["snake*"]),
    package_data={
        "snake.mcp.server": ["py.typed"],
    },
    include_package_data=True,
    install_requires=[
        "pytest",
        "flake8",
        "mypy",
        "pytest-asyncio",
        "pytest-cov",
        "mcp[cli]",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
