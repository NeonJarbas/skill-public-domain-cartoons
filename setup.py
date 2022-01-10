#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-pd-cartoons.jarbasai=skill_pd_cartoons:PublicDomainCartoonsSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-pd-cartoons',
    version='0.0.1',
    description='ovos public domain cartoons skill plugin',
    url='https://github.com/JarbasSkills/skill-public-domain-cartoons',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_pd_cartoons": ""},
    package_data={'skill_pd_cartoons': ['locale/*', 'ui/*']},
    packages=['skill_pd_cartoons'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
