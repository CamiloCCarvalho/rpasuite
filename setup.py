from setuptools import setup, find_packages

setup(
    name='rpa_suite',
    version='0.6.0',
    packages=find_packages(),
    description='Conjunto de ferramentas essenciais para RPA com Python, que facilitam o dia a dia de desenvolvimento.',
    long_description_content_type='text/markdown',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    author='Camilo Costa de Carvalho',
    author_email='camilo.carvalho@triasoftware.com.br',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='basic-tools, email-tools, email-validation, file-tools, simple-functions, rpa-tools, rpa-functions',
    install_requires=['loguru', 'colorama', 'email_validator'],
)
