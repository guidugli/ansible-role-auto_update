Ansible Role: auto_update
=========

An Ansible Role that install and configure packahes to perform automatic updates on RHEL/CentOS, Fedora and Debian/Ubuntu.

Requirements
------------

No requirements.

Role Variables
--------------

**Available variables are listed below, along with default values (see defaults/main.yml):**

    au_enable_auto_update: yes

Configure system to automatically update packages regularly If set to no, the role will disable the service (if installed) or do nothing (if not already installed).

    au_security_only: yes

If set to yes, only install security updates

    au_email_from: root

Origin email

    #au_email_to: admin@someorg.local

Who should receive the email

    au_download_only: no

If set to yes, the updates will be downloaded but not installed.
If set to no, updates will be downloaded and installed.

    #au_emit_via: stdio

How to send messages.  Valid options are stdio, email and motd.

    #au_command_format: "mail -s {subject} -r {email_from} {email_to}"

The shell command to use to send email. This is a Python format string, as used in str.format(). The format function will pass shell-quoted arguments called body, subject, email_from, email_to.

    #au_stdin_format: "{body}"

The contents of stdin to pass to the command. It is a format string with the same arguments as `command_format`.

    #au_email_server: localhost

Email server hostname or ip

    #au_system_name: mysystem

Name to use for this system in messages that are emitted.  Default is the hostname.

    #au_mail_report: only-on-error

Set this value to one of: "always", "only-on-error" or "on-change"

    #au_remove_old_kernel: yes

Remove unused automatically installed kernel-related packages (kernel images, kernel headers and kernel version locked tools).

    au_remove_new_unused_dependencies: yes

Do automatic removal of newly unused dependencies after the upgrade

    au_remove_unused_dependencies: no

Do automatic removal of unused packages after the upgrade (equivalent to apt-get autoremove)

    #au_automatic_reboot: no

Automatically reboot *WITHOUT CONFIRMATION* if the file /var/run/reboot-required is found after the upgrade

    #au_reboot_with_users: yes

Automatically reboot even if there are users currently logged in when Unattended-Upgrade::Automatic-Reboot is set to true

    #au_reboot_time: '02:00'

If automatic reboot is enabled and needed, reboot at the specific time instead of immediately. Default is "now".

    #au_syslog_enable: no

Enable logging to syslog. Default is False

    #au_syslog_facility: daemon

Specify syslog facility. Default is daemon


Dependencies
------------

No dependencies.

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: guidugli.auto_update }

License
-------

MIT / BSD

Author Information
------------------

This role was created in 2020 by Carlos Guidugli.
