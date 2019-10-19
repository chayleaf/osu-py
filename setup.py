import setuptools

with open("README.md", "r") as f:
	long_description = f.read()

setuptools.setup(
	name='osu.py',
	version='0.0.17',
	author='pavlukivan',
	author_email='ivanpavluk00@gmail.com',
	description='A multipurpose osu! library, aiming to cover practically any use case over time',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/pavlukivan/osu-py',
	packages=['osu'],
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3 :: Only',
		'Topic :: Games/Entertainment',
	],
	keywords='osu api osugame beatmap collection score db',
	install_requires=[],
	python_requires='>=3',
)
