from pathlib import Path
from wads.package_module import generate_package

root = Path(__file__).parent


if __name__ == '__main__':
    generate_package(
        module_path=root / 'real_dpp',
        install_requires=[
            'py2store',
            'omodel @ git+ssh://git@github.com/otosense/omodel.git',
            'olab @ git+ssh://git@github.com/otosense/olab.git',
        ],
        output_path=root / 'pkgs/real_dpp',
        glob_pattern='*.pkl',
        version='1.0.0',
    )
