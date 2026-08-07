import types


# Basic query tests

def test_query(fresh_db):
    fresh_db["dogs"].insert_all([{"name": "Cleo"}, {"name": "Pancakes"}])
    results = fresh_db.query("select * from dogs order by name desc")
    assert isinstance(results, types.GeneratorType)
    assert list(results) == [{'id':2, "name": "Pancakes"}, {'id':1, "name": "Cleo"}]


def test_execute_returning_dicts(fresh_db):
    # Like db.query() but returns a list, included for backwards compatibility
    # see https://github.com/simonw/sqlite-utils/issues/290
    fresh_db["test"].insert({"id": 1, "bar": 2}, pk="id")
    assert fresh_db.execute_returning_dicts("select * from test") == [
        {"id": 1, "bar": 2}
    ]

def test_query_no_update(fresh_db):
    """Test that a query that doesn't update the database:
    1) Returns an empty list and 2) Doesn't change the database"""
    fresh_db["message"].insert({"msg_type": "greeting", "content": "hello"})
    results = fresh_db.query("update message set msg_type='note' where msg_type='md'")
    assert list(results) == []
    assert list(fresh_db["message"].rows) == [{'id':1,"msg_type": "greeting", "content": "hello"}]
