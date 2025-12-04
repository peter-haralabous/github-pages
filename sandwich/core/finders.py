from django.contrib.staticfiles.finders import FileSystemFinder


class CustomFileSystemFinder(FileSystemFinder):
    """
    A custom staticfiles finder that excludes files that are handled by webpack.
    """

    def list(self, ignore_patterns):
        for path, storage in super().list(ignore_patterns):
            # NOTE-NG: these are very broad exclusions
            # we'll need to change our approach if we add css or js files that aren't handled by webpack
            if not path.startswith(("js/", "css/")):
                yield path, storage
