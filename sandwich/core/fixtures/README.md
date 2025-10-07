# Fixtures

## Django

https://docs.djangoproject.com/en/stable/topics/db/fixtures/

> A fixture is a collection of files that contain the serialized contents of the database. Each fixture has a unique name, and the files that comprise the fixture can be distributed over multiple directories, in multiple applications.

`make save-fixtures` will save the current state of selected models in the database to the repo.

`make load-fixtures` will load that state into your database.

These fixtures make use of [`natural keys`](https://docs.djangoproject.com/en/stable/topics/serialization/#natural-keys) to avoid issues with primary key values changing between different databases.

See also:
  - https://docs.djangoproject.com/en/stable/howto/initial-data/
  - https://docs.djangoproject.com/en/stable/topics/serialization/

## Pytest

pytest has a separate concept of [fixtures](https://docs.pytest.org/en/6.2.x/fixture.html)
