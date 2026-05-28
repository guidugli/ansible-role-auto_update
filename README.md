# Ansible Role: auto_update

[![CI](https://github.com/guidugli/ansible-role-auto_update/actions/workflows/CI.yml/badge.svg)](https://github.com/guidugli/ansible-role-auto_update/actions/workflows/CI.yml)
[![Release](https://github.com/guidugli/ansible-role-auto_update/actions/workflows/release.yml/badge.svg)](https://github.com/guidugli/ansible-role-auto_update/actions/workflows/release.yml)
[![Galaxy](https://img.shields.io/badge/Galaxy-guidugli.auto__update-blue)](https://galaxy.ansible.com/ui/standalone/roles/guidugli/auto_update/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Install and configure automatic package update tooling on Debian, Ubuntu, Fedora, and legacy yum-based systems.

## Overview

This role manages the platform-appropriate automatic update backend:

- **APT / unattended-upgrades** on Debian and Ubuntu
- **dnf-automatic** on dnf-based Fedora systems
- **dnf5-plugin-automatic** on dnf5-based Fedora systems
- **yum-cron** on legacy yum systems

The role is designed to stay consistent with the conventions used in the modernized role ecosystem:

- explicit public defaults in `defaults/main.yml`
- `meta/argument_specs.yml` for type and choice validation
- `tasks/assert.yml` for semantic validation
- clean `tasks/main.yml` validation + backend dispatch
- generator-first metadata flow for `meta/main.yml`
- shared Molecule layout with meaningful verification
- role behavior separated from play-level privilege escalation

## Features

- Enables or disables automatic updates through a single role toggle
- Supports security-only update mode where the backend supports it
- Manages unattended-upgrades on Debian and Ubuntu
- Manages dnf-automatic or dnf5 automatic tooling on Fedora
- Optionally manages a systemd timer override for dnf / dnf5 scheduling
- Keeps service and timer management container-friendly for Molecule idempotency
- Uses generated metadata and generated inventories from shared test data

## Requirements

- Ansible **2.14+**
- Python available on target hosts
- Privilege escalation capable play when package or configuration changes are required

## Supported platforms

The repository is structured around the latest shared matrix used across the modernized roles:

- Ubuntu 26.04 / 24.04
- Debian 13 / 12
- Fedora 44 / 43

Galaxy metadata is rendered from the shared matrix and converted to the correct platform version strings.

## Role variables

### Core toggle

```yaml
au_enable_auto_update: true
```

Enable or disable automatic updates.

When set to `false`, the role disables the relevant service or timer **only if** the corresponding package is already installed.

### Shared behavior

```yaml
au_security_only: true
au_email_from: root
au_email_to: null
```

### Fedora / Red Hat family behavior

```yaml
au_download_only: false
au_emit_via: null
au_command_format: null
au_stdin_format: null
au_email_server: null
au_system_name: null
au_redhat_reboot: null
```

### Fedora schedule control (`dnf` / `dnf5`)

```yaml
au_manage_schedule: false
au_timer_on_calendar: ''
au_timer_randomized_delay_sec: ''
au_timer_persistent: true
```

### Debian / Ubuntu unattended-upgrades behavior

```yaml
au_mail_report: null
au_remove_old_kernel: null
au_remove_new_unused_dependencies: true
au_remove_unused_dependencies: false
au_automatic_reboot: null
au_reboot_with_users: null
au_reboot_time: null
au_syslog_enable: null
au_syslog_facility: null
```

## Built-in package sets / important behavior

### APT backend

The role installs and manages:

- `unattended-upgrades`
- `/etc/apt/apt.conf.d/20auto-upgrades`
- `/etc/apt/apt.conf.d/50unattended-upgrades`
- `unattended-upgrades.service` enablement when systemd is present

### DNF / DNF5 backend

The role installs and manages:

- `dnf-automatic` or `dnf5-plugin-automatic`
- `/etc/dnf/automatic.conf`
- backend timer enablement when systemd is present
- optional systemd override files when schedule control is enabled

### Legacy YUM backend

The role retains `yum-cron` support for completeness, although it is outside the primary Molecule matrix.

## How it works

1. `meta/argument_specs.yml` validates supported options and base choices.
2. `tasks/assert.yml` validates semantic rules such as reboot time formatting and schedule requirements.
3. `tasks/main.yml` maps the detected package manager to the backend task file.
4. The selected backend configures packages, files, and service/timer enablement in an idempotent way.

## Usage examples

### Minimal example

```yaml
- name: Enable automatic updates
  hosts: all
  become: true
  roles:
    - role: guidugli.auto_update
```

### Security-only updates with email reporting

```yaml
- name: Configure security-only automatic updates
  hosts: all
  become: true
  roles:
    - role: guidugli.auto_update
      vars:
        au_enable_auto_update: true
        au_security_only: true
        au_email_from: root
        au_email_to: ops@example.local
        au_mail_report: only-on-error
```

### DNF timer override example

```yaml
- name: Configure automatic updates with explicit schedule
  hosts: fedora
  become: true
  roles:
    - role: guidugli.auto_update
      vars:
        au_manage_schedule: true
        au_timer_on_calendar: 'Mon..Fri 02:30'
        au_timer_randomized_delay_sec: '30m'
        au_timer_persistent: true
```

### Disable automatic updates

```yaml
- name: Disable automatic updates
  hosts: all
  become: true
  roles:
    - role: guidugli.auto_update
      vars:
        au_enable_auto_update: false
```

## Design notes

### Privilege escalation / become

This role does **not** force `become` inside the role tasks.

Recommended pattern:

- callers set `become: true` in the play when needed
- Molecule scenarios decide whether privilege escalation is appropriate for the scenario model

### Raw usage

This is **not** a pre-Python bootstrap role. Normal Ansible modules are used for role behavior.
Only Molecule prepare steps may use `raw` to bootstrap Python inside test containers.

### Idempotency

To keep containerized tests stable and idempotent:

- systemd handlers reconcile enablement instead of forcing runtime state transitions
- backend tasks avoid starting timers/services unnecessarily in container scenarios
- schedule override files are created and removed predictably

## Molecule testing

The repository is aligned to a shared Molecule layout:

```text
molecule/
  shared/
    vars.yml
    converge.yml
    verify.yml
  default/
  systemd/
```

### Run locally

```bash
./scripts/run_local.sh
```

Or run scenarios individually:

```bash
molecule test -s default
molecule test -s systemd
```

## Release workflow

Generated artifacts should come from the shared metadata flow rather than manual edits.

### Source of truth

- `molecule/shared/vars.yml`
- `templates/meta_main.yml.j2`

### Generated outputs

- `meta/main.yml`
- Molecule inventories

### Refresh generated artifacts

```bash
./scripts/update_release_metadata.sh
```

### Prepare a release

```bash
./scripts/release.sh --version v1.2.0 --message "Release v1.2.0"
```

## Repository structure

```text
defaults/
  main.yml
handlers/
  main.yml
meta/
  argument_specs.yml
  main.yml
molecule/
  shared/
  default/
  systemd/
scripts/
  render_inventory.py
  render_meta_main.py
  update_release_metadata.sh
  release.sh
tasks/
  main.yml
  assert.yml
  apt_autoupdate.yml
  dnf_autoupdate.yml
  dnf5_autoupdate.yml
  yum_autoupdate.yml
templates/
  Debian/
  Ubuntu/
  automatic.conf
  systemd_timer_override.conf.j2
  meta_main.yml.j2
```

## License

MIT

## Author

Carlos Guidugli
