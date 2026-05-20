from setuptools import setup, find_packages

setup(
    name="fishcast",
    version="1.0.0",
    description="钓鱼佬永不空军 - 钓鱼决策智能体引擎",
    author="eluckydog",
    packages=find_packages(),
    package_data={"fishcast": ["data/*.py"]},
    install_requires=[],
    entry_points={
        "console_scripts": [
            "fishcast=fishcast.__main__:main",
        ],
    },
    classifiers=[
        "Private :: Do Not Upload",
        "Programming Language :: Python :: 3",
    ],
)
