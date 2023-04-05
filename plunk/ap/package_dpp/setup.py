import os
import shutil
import subprocess
from distutils.command.sdist import sdist

from isee import generate_project_wheels
from setuptools import setup, Command
import setuptools.command.build_py


class CustomSdistCommand(sdist):
    """Custom sdist command to include wheels in the distribution"""

    description = 'create a source distribution tarball with embedded wheels'

    def run(self):

        # create a temporary directory to store the wheels
        project_dir = os.getcwd()
        wheel_generation_dir = os.path.join(project_dir, 'wheels')
        if os.path.exists(wheel_generation_dir):
            shutil.rmtree(wheel_generation_dir)
        os.mkdir(wheel_generation_dir)
        print(f'{project_dir=}, {wheel_generation_dir=}')
        generate_project_wheels(
            project_dir, wheel_generation_dir, github_credentails=None
        )

        # copy the wheels into the package directory
        for wheel_file in os.listdir(wheel_generation_dir):
            if wheel_file.endswith('.whl'):
                shutil.copy2(os.path.join(wheel_generation_dir, wheel_file), 'dist')

        # cleanup the temporary directory
        # shutil.rmtree(wheel_generation_dir)
        if self.dist_dir is None:
            self.dist_dir = 'dist'
        base_dir = self.distribution.get_fullname()
        print(f'{self.dist_dir=}')
        base_name = os.path.join(self.dist_dir, base_dir)
        print(f'{self.dist_dir=}, {base_dir=}, {base_name=}')

        # call the default sdist command to create the tar.gz file
        super().run()


class BuildPyCommand(setuptools.command.build_py.build_py):
    def run(self):
        import subprocess

        subprocess.check_call(
            ['pip', 'wheel', '--no-deps', '--wheel-dir', 'dist/wheels', '.']
        )
        setuptools.command.build_py.build_py.run(self)


setup(
    cmdclass={
        # 'build_py': BuildPyCommand,
        'sdist_wheel': CustomSdistCommand
    }
)
