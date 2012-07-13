import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages


if __name__ == '__main__':
    setup(
        name='edittag',
        version="1.1",
        description="Design and check sets of edit metric sequence tags.",
        author="Brant Faircloth",
        author_email="brant.faircloth+edittag@gmail.com",
        url="http://github.com/faircloth-lab/edittag/",
        license="http://www.opensource.org/licenses/BSD-3-Clause",
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Operating System :: OS Independent',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
             ],
        requires=['numpy(>=1.3)',],
        long_description=open('README.rst').read(),
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
