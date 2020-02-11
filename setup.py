from setuptools import setup


if __name__ == '__main__':
  name = 'pyslack'
  version = '0.0.1'
  setup(
      name=name,
      version=version,
      description='This is the {} module.'.format(name),
      author='Lyuwen Fu',
      url='https://github.com/lyuwen/pyslack',
      packages=[
        "pyslack",
        ],
      install_requires=[
        "slackclient>=2.5.0",
        ],
      provides=[
        name,
        ],
      entry_points={
        'console_scripts': ['pyslack=pyslack.pyslack:main'],
        },
      python_requires='>=3.6',
      )
