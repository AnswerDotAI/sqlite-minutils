import collections
import json

import pytest

from sqlite_minutils.db import NotFoundError


## Updates where nothing changes

def test_update_no_change(fresh_db):
    "Test updating a row with the same values it already has"
    table = fresh_db["table"]
    table.insert({"foo": "bar"})
    table.update(1, {"foo": "bar"})
    assert [{'id': 1, "foo": "bar"}] == table.update(1, {"foo": "bar"}).result
    table.update(1, {})
    assert [{'id': 1, "foo": "bar"}] == list(table.rows)

## Updates where something changes

def test_update_rowid_table(fresh_db):
    "Test updating a row that just got inserted, using the inserted row's last_pk as rowid"
    table = fresh_db["table"]
    rowid = table.insert({"foo": "bar", 'id': 1}).last_pk
    # Test that the Table.update method returns the correct value
    assert [{"foo": "baz", 'id': 1}] == table.update(rowid, {"foo": "baz"}).result
    # Test that the Table.rows property, which calls the DB, returns the correct value
    assert [{"foo": "baz", 'id': 1}] == list(table.rows)


def test_update_pk_table(fresh_db):
    "Like test_update_rowid_table, but with a user-specified primary key"
    table = fresh_db["table"]
    pk = table.insert({"foo": "bar", "id": 5}, pk="id").last_pk
    assert 5 == pk
    assert [{"id": 5, "foo": "baz"}] == table.update(pk, {"foo": "baz"}).result
    assert [{"id": 5, "foo": "baz"}] == list(table.rows)


def test_update_compound_pk_table(fresh_db):
    table = fresh_db["table"]
    record = table.insert({"id1": 5, "id2": 3, "v": 1}, pk=("id1", "id2")).result[0]
    pk = (record['id1'], record['id2'])
    assert (5, 3) == pk
    assert [{"id1": 5, "id2": 3, "v": 2}] == table.update(pk, {"v": 2}).result
    assert [{"id1": 5, "id2": 3, "v": 2}] == list(table.rows)


@pytest.mark.parametrize(
    "pk,update_pk",
    (
        (None, 2),
        (None, None),
        ("id1", None),
        ("id1", 4),
        (("id1", "id2"), None),
        (("id1", "id2"), 4),
        (("id1", "id2"), (4, 5)),
    ),
)
def test_update_invalid_pk(fresh_db, pk, update_pk):
    table = fresh_db["table"]
    table.insert({"id1": 5, "id2": 3, "v": 1}, pk=pk)
    with pytest.raises(NotFoundError):
        table.update(update_pk, {"v": 2})


def test_update_alter(fresh_db):
    table = fresh_db["table"]
    rowid = table.insert({"foo": "bar", 'id': 1}).last_pk
    table.update(rowid, {"new_col": 1.2}, alter=True)
    assert [{"foo": "bar", "new_col": 1.2, 'id': 1}] == list(table.rows)
    # Let's try adding three cols at once
    table.update(
        rowid,
        {"str_col": "str", "bytes_col": b"\xa0 has bytes", "int_col": -10},
        alter=True,
    )
    assert [
        {
            "foo": "bar",
            "new_col": 1.2,
            "str_col": "str",
            "bytes_col": b"\xa0 has bytes",
            "int_col": -10,
            'id': 1
        }
    ] == list(table.rows)


def test_update_alter_with_invalid_column_characters(fresh_db):
    table = fresh_db["table"]
    rowid = table.insert({"foo": "bar"}).last_pk
    with pytest.raises(AssertionError):
        table.update(rowid, {"new_col[abc]": 1.2}, alter=True)


def test_update_with_no_values_sets_last_pk(fresh_db):
    table = fresh_db.table("dogs", pk="id")
    table.insert_all([{"id": 1, "name": "Cleo"}, {"id": 2, "name": "Pancakes"}])
    table.update(1)
    assert table.last_pk == 1
    table.update(2)
    assert table.last_pk == 2
    with pytest.raises(NotFoundError):
        table.update(3)


@pytest.mark.parametrize(
    "data_structure",
    (
        ["list with one item"],
        ["list with", "two items"],
        {"dictionary": "simple"},
        {"dictionary": {"nested": "complex"}},
        collections.OrderedDict(
            [
                ("key1", {"nested": "complex"}),
                ("key2", "foo"),
            ]
        ),
        [{"list": "of"}, {"two": "dicts"}],
    ),
)
def test_update_dictionaries_and_lists_as_json(fresh_db, data_structure):
    fresh_db["test"].insert({"id": 1, "data": ""}, pk="id")
    fresh_db["test"].update(1, {"data": data_structure})
    row = fresh_db.execute("select id, data from test").fetchone()
    assert row[0] == 1
    assert data_structure == json.loads(row[1])
