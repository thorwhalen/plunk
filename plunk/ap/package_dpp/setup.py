import os
import shutil
from distutils.command.sdist import sdist
from setuptools import setup
from setuptools.command.install import install as _install


class CustomSdistCommand(sdist):
    """Custom sdist command to include wheels in the distribution"""

    description = 'create a source distribution tarball with embedded wheels'

    def _remove_wheels_from_install_requires(self, wheel_package_names):
        project_dir = os.getcwd()
        requirements_filepath = os.path.join(project_dir, 'requirements.txt')
        setup_cfg_filepath = os.path.join(project_dir, 'setup.cfg')
        if os.path.isfile(requirements_filepath):
            self._remove_lines(requirements_filepath, wheel_package_names)
        if os.path.isfile(setup_cfg_filepath):
            self._remove_lines(setup_cfg_filepath, wheel_package_names)

    def _remove_lines(self, filepath, exclude_lines):
        with open(filepath, 'r') as file:
            lines = file.readlines()

        # Find the line to delete and remove it
        new_lines = []
        for line in lines:
            if line.strip() not in exclude_lines:
                new_lines.append(line)
            else:
                print(f'Removing {line.strip()} from {filepath}')

        # Write the new lines back to the file
        with open(filepath, 'w') as file:
            file.writelines(new_lines)

    def initialize_options(self) -> None:
        super().initialize_options()
        # generating wheels here to modify setup.cfg before it's automatically copied
        from isee import generate_project_wheels

        if self.dist_dir is None:
            self.dist_dir = 'dist'
        if os.path.exists(self.dist_dir):
            print(f'Deleting {self.dist_dir}')
            shutil.rmtree(self.dist_dir)
        os.mkdir(self.dist_dir)

        # create a temporary directory to store the wheels
        project_dir = os.getcwd()
        wheel_generation_dir = os.path.join(project_dir, 'wheels')
        if os.path.exists(wheel_generation_dir):
            print(f'Deleting {wheel_generation_dir}')

            shutil.rmtree(wheel_generation_dir)
        os.mkdir(wheel_generation_dir)
        print('Generating dependency wheels')
        git_info = generate_project_wheels(
            project_dir, wheel_generation_dir, github_credentails=None
        )
        wheel_package_names = {g['name'] for g in git_info}
        # remove wheels from install_requires to skip pip dependency pre-check
        self._remove_wheels_from_install_requires(wheel_package_names)
        # copy the wheels into the package directory
        wheelhouse_dir = os.path.join(wheel_generation_dir, 'wheelhouse')
        for wheel_file in os.listdir(wheelhouse_dir):
            if wheel_file.endswith('.whl'):
                copy_wheel_file = os.path.join(wheelhouse_dir, wheel_file)
                shutil.copy2(copy_wheel_file, self.dist_dir)
                print(f'Copying to {copy_wheel_file}')

        # cleanup the temporary directory
        shutil.rmtree(wheel_generation_dir)

    def run(self):
        super().run()


class CustomInstallCommand(_install):
    def run(self):
        temp_dir = os.getcwd()

        # Install wheels from the dist directory of the tarball
        if os.path.isdir(dist_dir := os.path.join(temp_dir, 'dist')):
            for wheel in os.listdir(dist_dir):
                if wheel.endswith('.whl'):
                    print(f'Installing {wheel}')
                    self.spawn(
                        [
                            'pip',
                            'install',
                            os.path.join(dist_dir, wheel),
                            f'--find-links={dist_dir}',
                        ]
                    )

        # Run Normal Install
        _install.run(self)


setup(cmdclass={'install': CustomInstallCommand, 'sdist': CustomSdistCommand})
