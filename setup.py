import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages


if __name__ == '__main__':
    setup(
        name='edittag',
        version="1.0",
        description="Design and check sets of edit metric sequence tags.",
        author="Brant Faircloth",
        author_email="brant.faircloth+edittag@gmail.com ",
        url="http://baddna.github.com/edittag/",
        license="BSD",
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Operating System :: OS Independent',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
             ],
        requires=['NumPy (>=1.3)',],
        long_description=open('README.txt').read(),
        package_data = {
                # If any package contains *.txt or *.rst files, include them:
                '': ['*.txt', '*.rst'],
                'edittag': ['tests/test-data/*.txt'],
            },
        packages=['edittag',
                'edittag.tests',
                'edittag.primer3'
                ],
        scripts=['bin/add_tags_to_adapters.py',
                'bin/add_tags_to_primers.py',
                'bin/design_edit_metric_tags.py',
                'bin/estimate_sequencing_error_effects.py',
                'bin/get_tag_flows_for_454.py',
                'bin/validate_edit_metric_tags.py'
                ],

        
        )
