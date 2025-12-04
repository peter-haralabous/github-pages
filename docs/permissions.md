# Permissions Quick Start

Examples and usage patterns for role-based permissions in Sandwich.

## At a high level

We use [Django Guardian](https://django-guardian.readthedocs.io/en/stable/) to manage object level permissions.
A permission in Guardian is composed of three parts:
- permission string (eg. "view_patient")
- subject (User or Group)
- object (a model instance)

By default, the Guardian API is **explicit and declarative**. Although this can be verbose at times, it makes
permissions visible and easy to understand. For this reason, we should attempt to stick to Guardian defaults
as much as possible to avoid unnecessary abstractions.

## Use

Every model has the following default permissions out of the box: `view`, `add`, `change`, `delete`. You can
add additional custom permissions in a model's `Meta` class.

```py
class Task:
    ...

    class Meta:
        permissions = (
            ("complete_task", "Can complete a task."),
        )
```

### Assigning permissions

General rules for permission assignment:
- Use the provided `assign_perm` method from Django Guardian.
- It is best to apply default permissions to an object instance at the time of its creation.
- When assigning permissions, favour applying them to Roles (groups) over individual users.
- If a default permission like "change" isn't granular enough, use a custom permission.

```py
# Assign members of this group permissions to view this patient.
assign_perm("view_patient", role.group, patient_instance)
```

#### Handling add/create permissions

The `view`, `change`, and `delete` permissions all relate to the instance of an object, however, `add` is a
little bit different since it refers to an object instance that does not exist yet.

One option is to use `add` as a django global permission as opposed to an object permission. The problem with
this approach is that it applies the permission across all instances of `Patient` regardless of which org
they belong to. So for example, if we give a user the `add_patient` permission without an object target, that
user can create patients in all organizations.

Instead, we want to move the permission check "up" a level and attach it to the organization. This involves
introducing a custom permission on `Organization` called `create_patient`. This new permission reads as "this
user has permission to add new patients to this organization".

### Managing access

#### Views

Django Guardian provides us some view decorators, but these **should not** be used as they can introduce
information leaks, can be awkward to use on complex views, and make redundant db lookups.

Instead we can secure views by using our own `authorize_objects` decorator. This function extracts the object
id from the params, retrieves the object, checks whether the user has the permissions you specified, and then
injects the authorized object back into the view for use.

If the requesting user is not authorized, the decorator throws a 404.

```py
@authorize_objects([
    ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"]),
    ObjPerm(Organization, "organization_id", ["view_organization"]),
])
def patient_edit(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient) -> HttpResponse:
    ...
```

By default, the variable that gets injected into the view uses the name of the model (ie.
`Model._meta.model_name`). In some cases this is not always desired and can be overriden by passing a fourth
argument to the `ObjPerm` instance. For example:

```py
@authorize_objects([
    ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"], "custom_var_name"),
])
def patient_edit(request: AuthenticatedHttpRequest, custom_var_name: Patient) -> HttpResponse:
    ...
```

#### has_perm method

On any `User` or `Group`, you can use the `has_perm` method to check if the user has a given permission.

```py
request.user.has_perm("view_patient", patient)
```

#### Querysets

Guardian provides a powerful helper called `get_objects_for_user` which allows us to filter objects based
on a user's permissions.

```py
provider_encounters: QuerySet = get_objects_for_user(request.user, "view_encounter", Encounter)
```

`get_objects_for_user` returns a queryset that can be further filtered based on your needs.


### Omitting a view from permissions checks

The `test_all_views_permissioned` test in `sandwich/core/permissioned_views_test.py` checks our routes to
ensure they are secured with the `@authorize_objects` decorator. However, not all views use the decorator to
enforce permissions or are simply exempt from permission checks.

To allow a view to go unpermissioned, add its route to the `allowed_unpermissioned_routes` array.


## Resources

- [Django Guardian Docs](https://django-guardian.readthedocs.io/en/stable/)
