"""Errors for package manifest and block loading (no bbpm required)."""


class PackageLoadError(Exception):
    """Invalid or missing `.bbpackage` data, or failed block module load."""
