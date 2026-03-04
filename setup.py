# setup.py

from setuptools import setup, find_packages

setup(
    name='syswatch-pro',
    version='1.0.0',
    description='AI-Driven Distributed Systems Debugger - Professional Desktop Edition',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PySide6>=6.6.1',
        'pyqtgraph>=0.13.3',
        'fastapi>=0.109.0',
        'uvicorn>=0.27.0',
        'pydantic>=2.5.3',
        'requests>=2.31.0',
        'psutil>=5.9.7',
    ],
    extras_require={
        'dev': [
            'pyinstaller>=6.3.0',
            'pytest>=7.4.3',
            'black>=23.12.1',
        ]
    },
    entry_points={
        'console_scripts': [
            'syswatch=main:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)