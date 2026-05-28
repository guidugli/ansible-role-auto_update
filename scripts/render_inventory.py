#!/usr/bin/env python3
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VARS_FILE = ROOT / 'molecule' / 'shared' / 'vars.yml'
SCENARIOS = ('default', 'systemd')


def host_block(name: str, image: str, version: str) -> dict:
    return {
        name: {
            'ansible_connection': 'containers.podman.podman',
            'container_image': f'{image}:{version}',
            'container_command': 'sleep 1d',
        }
    }


def main() -> None:
    data = yaml.safe_load(VARS_FILE.read_text(encoding='utf-8'))
    matrix = data['platform_matrix']
    images = data['images']

    hosts: dict = {}
    for distro, versions in matrix.items():
        for version in versions:
            hostname = f"{distro}{str(version).replace('.', '')}"
            hosts.update(host_block(hostname, images[distro], str(version)))

    inventory = {
        'all': {
            'children': {
                'molecule': {
                    'hosts': hosts,
                }
            }
        }
    }

    rendered = yaml.safe_dump(
        inventory,
        sort_keys=False,
        explicit_start=True,
    )

    for scenario in SCENARIOS:
        output = ROOT / 'molecule' / scenario / 'inventory' / 'hosts.yml'
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding='utf-8')
        print(f'Wrote {output}')


if __name__ == '__main__':
    main()
