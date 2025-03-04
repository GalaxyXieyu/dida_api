from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="didatodolist",
    version="1.0.0",
    author="xieyu",
    author_email="523018705@qq.com",
    description="滴答清单(TickTick/Dida365) Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GalaxyXieyu/dida_api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "python-dateutil>=2.8.0",
        "pytz>=2024.1",
    ],
    keywords="dida365 ticktick todo task management api sdk",
) 