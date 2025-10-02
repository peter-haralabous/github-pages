## `# type: ignore[django-manager-missing]`

> [!NOTE]
> This is ignored on a per model basis as it appears that mypy cannot ignore errors globally that come from a plugin
> The plugin also doesn't appear to have an option to disable this check

This is required because django-stubs modifies the `Manager` during monkeypatching to add type support;
this breaks when libraries are defining their own managers without using django-stubs (like django-modeltranslations).

> [!WARNING]
> This also applies to the related managers that get defined on models with FK from translated models.

> I'm afraid it's not much to do other than ignoring the error until 
> <library> starts to export types. At least as far as I'm aware

See: https://github.com/typeddjango/django-stubs/issues/1023
