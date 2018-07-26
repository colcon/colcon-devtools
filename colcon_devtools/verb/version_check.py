# Copyright 2016-2018 Dirk Thomas
# Licensed under the Apache License, Version 2.0

import sys
from xmlrpc.client import ServerProxy

from colcon_core.entry_point import get_all_entry_points
from colcon_core.plugin_system import satisfies_version
from colcon_core.verb import VerbExtensionPoint
from pkg_resources import parse_version


class VersionCheckVerb(VerbExtensionPoint):
    """Compare local package versions with PyPI."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(VerbExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def main(self, *, context):  # noqa: D102
        distributions = set()
        all_entry_points = get_all_entry_points()
        for group in all_entry_points.values():
            for dist, _ in group.values():
                distributions.add(dist)

        pypi = ServerProxy('https://pypi.python.org/pypi')
        for dist in sorted(distributions, key=lambda d: d.project_name):
            versions = pypi.package_releases(dist.project_name)
            if not versions:
                print(
                    '{dist.project_name}: could not find package on PyPI'
                    .format_map(locals()), file=sys.stderr)
                continue

            latest_version = versions[0]
            if parse_version(latest_version) == parse_version(dist.version):
                print(
                    '{dist.project_name} {dist.version}: up-to-date'
                    .format_map(locals()))
                continue
            if parse_version(dist.version) < parse_version(latest_version):
                print(
                    '{dist.project_name} {dist.version}: newer version '
                    'available ({latest_version})'
                    .format_map(locals()))
                continue
            print(
                '{dist.project_name} {dist.version}: local version is newer '
                'than latest release ({latest_version})'
                .format_map(locals()))
            continue
