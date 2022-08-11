django-deepcopy
===============
Easily copy Django objects and their child objects, similar to Python's built-in `deepcopy`.

## What?
Using `django-deepcopy` on an object will copy the objects th
These are the objects that would be deleted when calling `.delete()` on the object (these can
be viewed without deleting anything, by clicking the "Delete"-button in the Django admin page
for the object. You will be shown a confirmation page, which lists the objects that will be
deleted.)

    from django_deepcopy import django_deepcopy

    class Bike(models.Model):
      id = models.UUIDField(primary_key=True, default=uuid.uuid4)


    class Wheel(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4)
        bike = models.ForeignKey(Bike, on_delete=models.CASCADE, related_name='wheels')


    old_bike = Bike.objects.create()
    wheels = [
        Wheel.objects.create(bike=old_bike),
        Wheel.objects.create(bike=old_bike),
    ]
    new_bike = django_deepcopy(old_bike)

    print(wheels[0] != new_bike.wheels.first())
    # Outputs: False


## Caveats

- Currently only works on models using UUIDs as primary keys.


## Tests
Run the tests by doing:

```bash
py.test tests/
````

### Updating models used in tests
The models used in the tests live in a Django app in `tests/testapp`.
If you add, remove, or make changes to those models run:

```bash
env DJANGO_SETTINGS_MODULE=tests.settings poetry run django-admin makemigrations testapp
````

and add the generated migrations.