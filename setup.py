from setuptools import setup, find_packages

setup(
    name='rpa_suite',
    version='1.5.4',
    packages=find_packages(),
    description='Conjunto de ferramentas essenciais para Automação RPA com Python, que facilitam o dia a dia de desenvolvimento.',
    long_description_content_type='text/markdown',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    author='Camilo Costa de Carvalho',
    author_email='camilo.carvalho@vettracode.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: RPA Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='basic-tools, email-tools, email-validation, file-tools, simple-functions, rpa-tools, rpa-functions, Tools, Rpa, Automation, RPA, Automação, Python, Ferramentas de RPA, Automação de Processos, Biblioteca Python para RPA, Bot, Robô, Ferramentas de automação, automation-tools, workflow-automation, rpa-framework, python-bots, automation-library, rpa-development, python-automation-tools',
    install_requires=['colorama', 'colorlog', 'email_validator', 'loguru', 'typing', 'pillow', 'pyautogui', 'requests', 'setuptools'],
    project_urls={
        "Código Fonte": "https://github.com/CamiloCCarvalho/rpasuite",
        "Documentação": "https://github.com/CamiloCCarvalho/rpasuite/wiki",
        "LinkedIn": "https://www.linkedin.com/in/camilocostac/",
    },
)
