"""Command-line entry point for the config Django project."""

import os
import sys


def main():
    """Execute Django management commands using this project settings."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
