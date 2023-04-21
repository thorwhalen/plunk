from pathlib import Path
from wads.package_module import generate_package

plunk_root = Path(__file__).parent.parent.parent

if __name__ == '__main__':
    generate_package(
        module_path=plunk_root / 'ap/package_dpp/test_dpp',
        install_requires=[
            'olab @ git+ssh://git@github.com/otosense/olab.git',
            'PySoundFile',
            'numpy',
            'meshed',
        ],
        output_path=plunk_root / 'ap/package_dpp/test_dpp_package',
        glob_pattern='*.pkl',
        version='1.0.0',
    )
