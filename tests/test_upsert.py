from sqlite_minutils.db import PrimaryKeyRequired
import pytest


def test_upsert(fresh_db):
    table = fresh_db["table"]
    table.insert({"id": 1, "name": "Cleo"}, pk="id")
    table.upsert({"id": 1, "age": 5}, pk="id", alter=True)
    # Check the returned value
    assert table.result == [{"id": 1, "name": "Cleo", "age": 5}]
    # Check the database itself
    assert list(table.rows) == [{"id": 1, "name": "Cleo", "age": 5}]
    assert table.last_pk == 1


def test_upsert_all(fresh_db):
    table = fresh_db["table"]
    table.upsert_all([{"id": 1, "name": "Cleo"}, {"id": 2, "name": "Nixie"}], pk="id")
    table.upsert_all([{"id": 1, "age": 5}, {"id": 2, "age": 5}], pk="id", alter=True)
    # Check the returned value
    assert table.result == [
        {"id": 1, "name": "Cleo", "age": 5},
        {"id": 2, "name": "Nixie", "age": 5},
    ]
    # Check the database itself
    assert list(table.rows) == [
        {"id": 1, "name": "Cleo", "age": 5},
        {"id": 2, "name": "Nixie", "age": 5},
    ]
    assert table.last_pk is None


def test_upsert_all_single_column(fresh_db):
    table = fresh_db["table"]
    result = table.upsert_all([{"name": "Cleo"}], pk="name").result
    # Check the returned value
    assert result == [{"name": "Cleo"}]
    # Check the database itself
    assert list(table.rows) == [{"name": "Cleo"}]
    assert table.pks == ["name"]


def test_upsert_all_not_null(fresh_db):
    # https://github.com/simonw/sqlite-utils/issues/538
    fresh_db["comments"].upsert_all(
        [{"id": 1, "name": "Cleo"}],
        pk="id",
        not_null=["name"],
    )
    # Check the returned value
    assert fresh_db["comments"].result == [{"id": 1, "name": "Cleo"}]
    # Check the database itself
    assert list(fresh_db["comments"].rows) == [{"id": 1, "name": "Cleo"}]


def test_upsert_error_if_no_pk(fresh_db):
    table = fresh_db["table"]
    with pytest.raises(PrimaryKeyRequired):
        table.upsert_all([{"id": 1, "name": "Cleo"}])
    with pytest.raises(PrimaryKeyRequired):
        table.upsert({"id": 1, "name": "Cleo"})


def test_upsert_with_hash_id(fresh_db):
    table = fresh_db["table"]
    table.upsert({"foo": "bar"}, hash_id="pk")
    # Check the returned value
    assert [{"pk": "a5e744d0164540d33b1d7ea616c28f2fa97e754a", "foo": "bar"}] == list(
        table.result
    )
    # Check the database itself
    assert [{"pk": "a5e744d0164540d33b1d7ea616c28f2fa97e754a", "foo": "bar"}] == list(
        table.rows
    )
    assert "a5e744d0164540d33b1d7ea616c28f2fa97e754a" == table.last_pk


@pytest.mark.parametrize("hash_id", (None, "custom_id"))
def test_upsert_with_hash_id_columns(fresh_db, hash_id):
    table = fresh_db["table"]
    table.upsert({"a": 1, "b": 2, "c": 3}, hash_id=hash_id, hash_id_columns=("a", "b"))
    # Check the returned value
    assert table.result == [
        {
            hash_id or "id": "4acc71e0547112eb432f0a36fb1924c4a738cb49",
            "a": 1,
            "b": 2,
            "c": 3,
        }
    ]    
    # Check the database itself  
    assert list(table.rows) == [
        {
            hash_id or "id": "4acc71e0547112eb432f0a36fb1924c4a738cb49",
            "a": 1,
            "b": 2,
            "c": 3,
        }
    ]
    assert table.last_pk == "4acc71e0547112eb432f0a36fb1924c4a738cb49"
    table.upsert({"a": 1, "b": 2, "c": 4}, hash_id=hash_id, hash_id_columns=("a", "b"))
    # Check the returned value
    assert table.result == [
        {
            hash_id or "id": "4acc71e0547112eb432f0a36fb1924c4a738cb49",
            "a": 1,
            "b": 2,
            "c": 4,
        }
    ]
    # Check the database itself
    assert list(table.rows) == [
        {
            hash_id or "id": "4acc71e0547112eb432f0a36fb1924c4a738cb49",
            "a": 1,
            "b": 2,
            "c": 4,
        }
    ]


def test_upsert_compound_primary_key(fresh_db):
    table = fresh_db["table"]
    table.upsert_all(
        [
            {"species": "dog", "id": 1, "name": "Cleo", "age": 4},
            {"species": "cat", "id": 1, "name": "Catbag"},
        ],
        pk=("species", "id"),
    )
    assert table.last_pk is None
    table.upsert({"species": "dog", "id": 1, "age": 5}, pk=("species", "id"))
    assert ("dog", 1) == table.last_pk
    # Check the returned value
    # Only one record was changed, so we don't look at all the rows
    assert [
        {"species": "dog", "id": 1, "name": "Cleo", "age": 5},
    ] == table.result
    # Check the database itself, the `.row` propery returns all rows
    assert [
        {"species": "dog", "id": 1, "name": "Cleo", "age": 5},
        {"species": "cat", "id": 1, "name": "Catbag", "age": None},
    ] == list(table.rows)
    # .upsert_all() with a single item should set .last_pk
    table.upsert_all([{"species": "cat", "id": 1, "age": 5}], pk=("species", "id"))
    assert ("cat", 1) == table.last_pk
