from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="zotero2md",
    version="0.1.0",
    description="Zotero to Markdown Export Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/zotero2md",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    keywords="zotero markdown export obsidian logseq bibtex json csv",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "jinja2>=3.0",
        "pyyaml>=5.0",
        "html2text>=2020.0",
        "requests>=2.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "zotero2md=zotero2md.main:main",
        ],
    },
)