from __future__ import absolute_import, unicode_literals

from virtualenv.app_data import AppDataDiskFolder, TempAppData

from ..wheels.embed import get_embed_wheel
from .periodic_update import periodic_update
from .util import Version, Wheel, discover_wheels


def from_bundle(distribution, version, for_py_version, search_dirs, app_data, do_periodic_update):
    """
    Load the bundled wheel to a cache directory.
    """
    of_version = Version.of_version(version)
    wheel = load_embed_wheel(app_data, distribution, for_py_version, of_version)

    if version != Version.embed:
        # 2. check if we have upgraded embed
        if isinstance(app_data, AppDataDiskFolder) and not isinstance(app_data, TempAppData):
            wheel = periodic_update(distribution, for_py_version, wheel, search_dirs, app_data, do_periodic_update)

        # 3. acquire from extra search dir
        found_wheel = from_dir(distribution, of_version, for_py_version, search_dirs)
        if found_wheel is not None:
            if wheel is None:
                wheel = found_wheel
            elif found_wheel.version_tuple > wheel.version_tuple:
                wheel = found_wheel
    return wheel


def load_embed_wheel(app_data, distribution, for_py_version, version):
    wheel = get_embed_wheel(distribution, for_py_version)
    if wheel is not None:
        version_match = version == wheel.version
        if version is None or version_match:
            with app_data.ensure_extracted(wheel.path, lambda: app_data.house) as wheel_path:
                wheel = Wheel(wheel_path)
        else:  # if version does not match ignore
            wheel = None
    return wheel


def from_dir(distribution, version, for_py_version, directories):
    """
    Load a compatible wheel from a given folder.
    """
    for folder in directories:
        for wheel in discover_wheels(folder, distribution, version, for_py_version):
            return wheel
    return None
