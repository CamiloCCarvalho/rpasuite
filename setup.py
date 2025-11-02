from setuptools import find_packages, setup

setup(
    name="rpa_suite",
    version="1.6.6",
    packages=find_packages(),
    description="Comprehensive Python toolkit for RPA automation: email, logging, database tracking, browser automation, OCR, desktop automation, and more. Essential utilities for building robust automation workflows with Selenium, Botcity, and custom solutions.",
    long_description_content_type="text/markdown",
    long_description=open("README.md", encoding="utf-8").read(),  # pylint: disable=consider-using-with
    author="Camilo Costa de Carvalho",
    author_email="camilo.costa1993@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Office/Business",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "Topic :: Utilities",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Communications :: Email",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Natural Language :: English",
        "Natural Language :: Portuguese (Brazilian)",
    ],
    keywords=(
        "rpa robotic-process-automation automation python "
        "selenium botcity browser-automation web-automation "
        "email smtp email-validation email-automation "
        "logging loguru file-operations screenshot screen-capture "
        "database sqlite postgresql mysql execution-tracking "
        "ocr document-conversion ai-ml computer-vision "
        "desktop-automation pyautogui gui-automation "
        "parallel-processing async async-await threading "
        "workflow-automation task-automation process-automation "
        "bot robot automation-tools automation-framework "
        "python-automation rpa-tools rpa-framework python-bots "
        "time-management scheduling cron job-scheduling "
        "data-validation regex pattern-matching text-processing "
        "file-management directory-management temp-files "
        "console-output colored-output terminal-utilities "
        "automation-library automation-suite rpa-development "
        "automação rpa automação-de-processos ferramentas-rpa "
        "biblioteca-python python-library"
    ),
    install_requires=[
        "colorama",
        "colorlog",
        "email_validator",
        "loguru",
        "typing",
        "pillow",
        "pyautogui",
        "requests",
        "opencv-python",
    ],
    python_requires=">=3.11",
    project_urls={
        "Homepage": "https://github.com/CamiloCCarvalho/rpasuite",
        "Documentation": "https://github.com/CamiloCCarvalho/rpasuite/wiki",
        "Source": "https://github.com/CamiloCCarvalho/rpasuite",
        "Tracker": "https://github.com/CamiloCCarvalho/rpasuite/issues",
        "LinkedIn": "https://www.linkedin.com/in/camilocostac/",
    },
)
