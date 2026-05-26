# Ansible Role: `auto_update`

Install and configure automatic package update tooling on Debian, Ubuntu, and Fedora systems.

This role is designed to:
- enable or disable automatic system updates
- configure unattended upgrades on Debian/Ubuntu
- configure dnf automatic updates on Fedora
- optionally keep update notifications and reboot behavior under policy control
- support the shared Molecule matrix used across the other modernized roles

---

## Features

- Installs the required automatic update package for the target platform
- Configures Debian/Ubuntu `unattended-upgrades`
- Configures Fedora `dnf-automatic` or `dnf5-automatic` depending on the detected package manager
- Can disable the service/timer if automatic updates are not desired and the package is already installed
- Supports security-only update mode where available
- Supports optional email/syslog/reporting/reboot settings
- Uses a platform-aware backend selected from the detected package manager

---

## Requirements

- Ansible >= 2.14
- Python available on target hosts
- Root or privilege escalation capability to manage packages, services, and configuration files

---

## Supported platforms

This repository is structured to support the latest two:
- Ubuntu LTS releases
- Debian releases
- Fedora releases

The current shared Molecule matrix includes:
- Ubuntu 26.04 / 24.04
- Debian 13 / 12
- Fedora 44 / 43

---

## Recommended Galaxy metadata

### Description

Recommended role description:

> Install and configure automatic package update tooling on Debian, Ubuntu, and Fedora systems.

### Recommended `galaxy_tags`

```yaml
galaxy_tags:
  - updates
  - automatic
  - patching
  - security
  - unattended
  - apt
  - dnf
  - linux
  - maintenance
```

---

## Role Variables

## Default Variables (`defaults/main.yml`)

### Core toggle

#### `au_enable_auto_update`
```yaml
au_enable_auto_update: yes
```
Enable or disable automatic updates.

If set to `no`, the role disables the relevant service/timer only when the related package is already installed.

---

### Shared behavior

#### `au_security_only`
```yaml
au_security_only: yes
```
Limit updates to security updates when supported by the backend.

#### `au_email_from`
```yaml
au_email_from: root
```
Sender address used in update notifications.

#### `au_email_to`
```yaml
# au_email_to: admin@someorg.local
```
Optional recipient address for update notifications.

---

### Red Hat / Fedora-related settings

#### `au_download_only`
```yaml
au_download_only: no
```
If `yes`, download updates without applying them.

#### `au_emit_via`
```yaml
# au_emit_via: stdio
```
Notification channel used by automatic update tooling.
Valid values:
- `stdio`
- `email`
- `motd`

#### `au_command_format`
```yaml
# au_command_format: "mail -s -r "
```
Command format used for command-based mail emitters.

#### `au_stdin_format`
```yaml
# au_stdin_format: ""
```
Standard input format used with command-based emitters.

#### `au_email_server`
```yaml
# au_email_server: localhost
```
SMTP server hostname or IP.

#### `au_system_name`
```yaml
# au_system_name: mysystem
```
Friendly system name used in notifications.

#### `au_redhat_reboot`
```yaml
# au_redhat_reboot: never
```
Reboot policy after updates on Red Hat family systems.
Valid values:
- `never`
- `when-changed`
- `when-needed`

---

### Debian / Ubuntu unattended-upgrades settings

#### `au_mail_report`
```yaml
# au_mail_report: only-on-error
```
Mail reporting policy.
Valid values:
- `always`
- `only-on-error`
- `on-change`

#### `au_remove_old_kernel`
```yaml
# au_remove_old_kernel: yes
```
Remove unused automatically installed kernel-related packages.

#### `au_remove_new_unused_dependencies`
```yaml
au_remove_new_unused_dependencies: yes
```
Remove newly unused dependencies after upgrade.

#### `au_remove_unused_dependencies`
```yaml
au_remove_unused_dependencies: no
```
Remove unused packages after upgrade.

#### `au_automatic_reboot`
```yaml
# au_automatic_reboot: no
```
Automatically reboot when unattended-upgrades determines a reboot is required.

#### `au_reboot_with_users`
```yaml
# au_reboot_with_users: yes
```
Allow automatic reboot even if users are currently logged in.

#### `au_reboot_time`
```yaml
# au_reboot_time: '02:00'
```
Scheduled automatic reboot time.
Valid values:
- `now`
- `HH:MM`

#### `au_syslog_enable`
```yaml
# au_syslog_enable: no
```
Enable unattended-upgrades syslog logging.

#### `au_syslog_facility`
```yaml
# au_syslog_facility: daemon
```
Syslog facility used by unattended-upgrades.

---

## Validation model

This role uses a two-layer validation approach:

1. **`meta/argument_specs.yml`**
   - validates supported variables
   - checks types and base choices

2. **`tasks/assert.yml`**
   - validates additional semantic constraints such as reboot time format and optional non-empty string variables

---

## Backend behavior

The role selects an implementation based on the detected package manager:

- `apt` -> `unattended-upgrades`
- `dnf` -> `dnf-automatic`
- `dnf5` -> `dnf5-plugin-automatic`
- `yum` -> legacy `yum-cron` support retained for completeness

---

## Example Playbook

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

---

## What the role configures

### Debian / Ubuntu

- installs `unattended-upgrades` when enabled
- manages:
  - `/etc/apt/apt.conf.d/20auto-upgrades`
  - `/etc/apt/apt.conf.d/50unattended-upgrades`
- enables or disables `unattended-upgrades.service`

### Fedora (`dnf` / `dnf5`)

- installs the related automatic update package when enabled
- manages:
  - `/etc/dnf/automatic.conf`
- enables or disables the related timer:
  - `dnf-automatic.timer`
  - `dnf5-automatic.timer`

### Legacy yum backend

- retains optional `yum-cron` support for compatibility outside the current main matrix

---

## Testing

This role uses **Molecule + Podman** and the same shared/default/systemd scenario layout used by the other updated roles.

### Scenarios
- `default`
- `systemd`

### Run locally

```bash
./scripts/run_local.sh
```

or individually:

```bash
molecule test -s default
molecule test -s systemd
```

---

## Release metadata workflow

Like the other modernized roles, this repository uses generated metadata based on the shared Molecule matrix.

### Source of truth

```text
molecule/shared/vars.yml
```

This drives:
- tested platforms
- generated inventories
- generated `meta/main.yml`

### Refresh metadata

```bash
./scripts/update_release_metadata.sh
```

### Prepare a release

```bash
./scripts/release.sh --version v1.2.0 --message "Release v1.2.0"
```

---

## Relevant project structure

```text
defaults/
  main.yml

tasks/
  main.yml
  assert.yml
  apt_autoupdate.yml
  dnf_autoupdate.yml
  dnf5_autoupdate.yml
  yum_autoupdate.yml

handlers/
  main.yml

templates/
  Debian/
  Ubuntu/
  automatic.conf
  meta_main.yml.j2

meta/
  main.yml
  argument_specs.yml

molecule/
  shared/
  default/
  systemd/
```

---

## Notes from the repository review

A few current repository details are worth correcting when you apply the generated files:

- the current `templates/meta_main.yml.j2` still has the wrong `role_name` (`chrony`) and unrelated chrony/time-sync tags
- the current `molecule/shared/verify.yml` is still copied from the audit role and should be replaced later with an auto-update-specific verifier
- the current role-level task flow still relies on older `become`/dispatch patterns that can be simplified with `validate_argument_spec` and backend mapping

---

## License

MIT

---

## Author

Carlos Guidugli
