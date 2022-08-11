import json
import logging
import re
from io import StringIO
from uuid import uuid4

from django.apps import apps
from django.contrib.admin.utils import NestedObjects
from django.core import serializers
from django.db import DEFAULT_DB_ALIAS, connections, router, transaction
from django.db.models import ForeignKey, ManyToManyField, OneToOneField

SERIALIZATION_FORMAT = 'json'
EXCLUDED_APPS: list[str] = []
EXCLUDED_MODELS: list[str] = []
USING = DEFAULT_DB_ALIAS
USE_NATURAL_PRIMARY_KEYS = False
USE_NATURAL_FOREIGN_KEYS = False

# from django.contrib import admin, auth
# IGNORED_MODELS = [
#     admin.models.LogEntry,
#     auth.models.Group,
#     auth.models.Permission,
# ]

logger = logging.getLogger(__name__)

# The techically correct pattern for UUID v4 is:
# r'[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}'
#
# However, we just do the naive thing here.
RE_UUID_PATTERN = r'[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}'
RE_UUID = re.compile(RE_UUID_PATTERN)


def get_all_related_objects(obj, ignored_models=None, dangling_models=None):
    if ignored_models is None:
        ignored_models = []
    if dangling_models is None:
        dangling_models = []

    collector = NestedObjects(using=USING)
    collector.collect([obj])
    related_objects = collector.model_objs
    all_models = list(set(related_objects.keys()))  # noqa: F841

    # `all_models` includes pseudo-models representing M2M relationships like `Group.member`
    # which the real Django `dumpdata` does not output. It instead stores those M2M relations
    # directly on the serialized `Group`-model. Therefore we use `dumped_models` instead, which
    # doesn't include these pseudo-models.
    dumped_models = set(apps.get_models())
    if ignored_models:
        dumped_models -= set(ignored_models)

    if USE_NATURAL_FOREIGN_KEYS:
        dumped_models = serializers.sort_dependencies(dumped_models, allow_cycles=True)

    all_related_objects = {**related_objects}

    for model in dangling_models:
        dangling_related_objects = get_referenced_objects_of_type(
            all_related_objects, model
        )
        all_related_objects = {**all_related_objects, **dangling_related_objects}
        dumped_models.add(model)

    all_objs = [
        obj for model in dumped_models for obj in all_related_objects.get(model, [])
    ]

    return all_objs


def get_referenced_objects_of_type(all_related_objects, model, filtered_models=None):
    all_models = apps.get_models()
    object_fields = []

    for m in all_models:
        for field in m._meta.fields:
            if isinstance(field, ForeignKey) and field.related_model == model:
                object_fields.append((m, field))
            elif isinstance(field, OneToOneField) and field.related_model == model:
                object_fields.append((m, field))
            elif isinstance(field, ManyToManyField) and field.related_model == model:
                object_fields.append((m, field))
            elif field.related_model == model:
                raise 'Unknown related field'

    object_ids = []
    for m, field in object_fields:
        for obj in all_related_objects.get(m, []):
            if isinstance(field, ForeignKey) or isinstance(field, OneToOneField):
                object_ids.append(getattr(obj, f'{field.name}_id'))
            elif isinstance(field, ManyToManyField):
                object_ids += getattr(obj, field.name).values_list('id', flat=True)
    objects = model._base_manager.filter(pk__in=object_ids)
    collector = NestedObjects(using='default')
    collector.collect(objects)
    related_objects = collector.model_objs
    if filtered_models:
        # Filter out all models not in `filtered_models`
        return {m: v for m, v in related_objects.items() if m in filtered_models}
    else:
        return related_objects


def create_new_pks_for_objects(objs, unique_field_generators):
    if unique_field_generators is None:
        unique_field_generators = {}

    old_id_to_new_id_map = {}
    for obj in objs:
        old_pk = obj['pk']
        if type(old_pk) is int:
            # Skip integer primary keys
            continue
        elif old_pk in old_id_to_new_id_map:
            continue
        else:
            old_id_to_new_id_map[old_pk] = str(uuid4())

    def transform_pk(value):
        if type(value) is str:
            m = RE_UUID.match(value)
            if m:
                try:
                    old_id = m.group(0)
                    new_id = old_id_to_new_id_map[old_id]
                    return value.replace(value, new_id)
                except KeyError:
                    raise
        return value

    for obj in objs:
        old_pk = obj['pk']

        # Transform reference field to use the new primary keys
        for field, value in obj['fields'].items():
            if (obj['model'], field) in unique_field_generators:
                obj['fields'][field] = unique_field_generators[(obj['model'], field)](
                    obj['fields'][field]
                )
            elif type(value) is list:
                obj['fields'][field] = [transform_pk(v) for v in obj['fields'][field]]
            elif type(value) is str:
                obj['fields'][field] = transform_pk(obj['fields'][field])
            # if (
            #     type(value) is list
            #     and value
            #     and type(value[0]) is str
            #     and RE_UUID.match(value[0])
            # ):
            #     for i, subvalue in enumerate(value):
            #         m = RE_UUID.match(subvalue)
            #         new_id = old_id_to_new_id_map[m.group(0)]
            #         [i] = subvalue.replace(subvalue, new_id)
            # if type(value) is str:
            #     m = RE_UUID.match(value)
            #     if m:
            #         new_id = old_id_to_new_id_map[m.group(0)]
            #         obj['fields'][field] = value.replace(value, new_id)

        # Use new primary key -- we transform this last to ease debugging
        # so that the old primary key is available if an exception is raised
        # when transforming the fields.
        if type(old_pk) is str:
            # Only transform string primary keys (assumed to be UUIDs here)
            obj['pk'] = old_id_to_new_id_map[old_pk]

    return objs, old_id_to_new_id_map


def insert_serialized_objects_into_db(objs):
    deserialization_stream = StringIO()
    json.dump(objs, deserialization_stream)
    deserialization_stream.seek(0)

    copied_objects = serializers.deserialize(
        SERIALIZATION_FORMAT,
        deserialization_stream,
        using=USING,
        # ignorenonexistent=self.ignore,
        handle_forward_references=True,
    )

    # From Django's built-in `loaddata`-command
    connection = connections[USING]
    objs_with_deferred_fields = []
    logger.debug('Starting atomic transaction')
    with transaction.atomic(using=USING):
        with connection.constraint_checks_disabled():
            for obj in copied_objects:
                if (
                    obj.object._meta.app_config in EXCLUDED_APPS
                    or type(obj.object) in EXCLUDED_MODELS
                ):
                    continue
                if router.allow_migrate_model(USING, obj.object.__class__):
                    # We use `model.objects.bulk_create()` instead of `obj.save()`
                    # to ensure that we fail on duplicate primary keys
                    # - this can happen for e.g.
                    #   through-"models" which have integer primary keys. In that case, we want to make
                    #   sure we don't overwrite existing groups, which
                    #   `obj.save()` does without erroring.
                    if type(obj.object.pk) is int and obj.object._meta.label in (
                        # Add integer PK models here
                    ):
                        # We assume here that there are no external references (e.g. ForeignKeys) to integer
                        # primary keys, and simply create new primary keys here without updating references.
                        obj.object.pk = None
                    logger.debug(f'  Bulk creating {obj.object}...')
                    obj.object._meta.model._base_manager.bulk_create([obj.object])
                    # We _also_ need to call `obj.save()` -- `obj` here is a `DeserializedObject` which
                    # contains and saves `ManyToMany`-relations like `Course.students` and `Course.teachers`.
                    logger.debug('  Done')
                    logger.debug(f'  Saving {obj.object}...')
                    obj.save(using=USING)
                    logger.debug('  Done')
                if obj.deferred_fields:
                    objs_with_deferred_fields.append(obj)

            logger.debug('  Saving deferred fields...')
            for obj in objs_with_deferred_fields:
                obj.save_deferred_fields(using=USING)
            logger.debug('  Done')
    logger.debug('  Done')

    # Since we disabled constraint checks, we must manually check for
    # any invalid keys that might have been added
    dumped_models = set(apps.get_models())
    table_names = [model._meta.db_table for model in dumped_models]
    logger.debug('Checking constraints...')
    connection.check_constraints(table_names=table_names)
    logger.debug('Done')


def django_deepcopy(
    obj, ignored_models=None, dangling_models=None, unique_field_generators=None
):

    ###### Step 1: Collect all objects related to `obj` #########
    all_objs = get_all_related_objects(obj, ignored_models, dangling_models)

    ###### Step 2: Serialize all collected objects #########
    object_count = len(all_objs)
    serialization_stream = StringIO()
    serializers.serialize(
        SERIALIZATION_FORMAT,
        # sorted(all_related_objects, key=lambda obj: model_order[obj.model]),
        all_objs,
        use_natural_foreign_keys=USE_NATURAL_FOREIGN_KEYS,
        use_natural_primary_keys=USE_NATURAL_PRIMARY_KEYS,
        stream=serialization_stream,
        object_count=object_count,
    )
    serialization_stream.seek(0)
    objs = json.load(serialization_stream)

    ###### Step 3: Create new IDs/pks for the objects #########
    objs, old_new_mapping = create_new_pks_for_objects(
        objs, unique_field_generators=unique_field_generators
    )

    # Get the PK of the copy of `obj`
    new_obj_id = old_new_mapping[str(obj.id)]

    ###### Step 4: Load serialized objects and insert into the database #########
    insert_serialized_objects_into_db(objs)

    new_obj = obj._meta.model.objects.get(id=new_obj_id)
    return new_obj
