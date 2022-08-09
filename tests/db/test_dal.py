import pytest

from vimania.db.dal import Todo, DAL, metadata
from vimania.environment import config


@pytest.fixture()
def dal_pristine():
    dal = DAL(env_config=config)
    dal.sim_results_db_url = "sqlite:///:memory:"
    with dal as dal:
        # noinspection PyProtectedMember
        metadata.create_all(dal._sql_alchemy_db_engine)
        yield dal


def test_reset_db(dal):
    _ = None


# noinspection PyTypeChecker,PyUnresolvedReferences
# @pytest.mark.skip("get real data")
def test_get_todo_tag(dal):
    results = dal.get_todos(fts_query="aaa")
    # for result in results:
    #     print(f"{result.use_case}, {result.reason}, {result.strategy}")
    assert len(results) > 0
    assert isinstance(results[0], Todo)


def test_get_todo_by_id(dal):
    bm = dal.get_todo_by_id(id_=1)
    assert isinstance(bm, Todo)
    assert bm.id == 1


def test_get_todo_by_id_non_existing(dal):
    bm = dal.get_todo_by_id(id_=999)
    assert isinstance(bm, Todo)
    assert bm.id is None


def test_get_todo_raw(dal):
    bms = dal.get_todos(fts_query="")
    assert len(bms) >= 5


def test_get_xxxxx(dal):
    # this is the testing entry in bm.db
    bms = dal.get_todos(fts_query="xxxxx")
    assert len(bms) == 1
    assert bms[0].tags == ",ccc,vimania,yyy,"


def test_get_duplicates(dal):
    # this is the testing entry in bm.db
    bms = dal.get_todos(fts_query="todo 5")
    assert len(bms) == 2
    _ = None


def test_get_todos(dal):
    todo = dal.get_todos(fts_query="xxxxx")[0]
    assert isinstance(todo, Todo)
    assert todo.tags == ",ccc,vimania,yyy,"


def test_update_bm(dal):
    todo = dal.get_todos(fts_query="xxxxx")[0]
    assert todo.tags == ",ccc,vimania,yyy,"

    todo.tags = ",bla,"
    result = dal.update_todo(todo)

    assert dal.get_todos(fts_query="xxxxx")[0].tags == ",bla,"
    assert result == 1


def test_insert_bm(dal):
    bm = Todo(
        todo="- [ ] xxxxx",
        metadata="metadata",
        tags=",aaa,bbb,ccc,",
        desc="description",
        path="newpath",
        flags=0,
        # created_at=datetime.utcnow(),
    )
    lastrowid = dal.insert_todo(bm)

    assert dal.get_todos(fts_query="xxxxx")[0].tags == ",aaa,bbb,ccc,"
    assert lastrowid == 13


def test_delete_todo(dal):
    result = dal.delete_todo(id=1)
    print(result)
    assert dal.get_todos(fts_query="xxxxx")[0].id is None


def test_split_tags(dal):
    bm = Todo(
        todo="- [ ] xxxxxxxxxxxxx",
        metadata="metadata",
        tags=",aaa,bbb,",
        desc="description",
        flags=0,
    )
    tags = bm.split_tags
    assert "" not in tags


@pytest.mark.parametrize(
    ("tag", "result"), (("ccc", ["aaa", "bbb", "ccc", "vimania", "yyy"]),)
)
def test_get_related_tags(dal, tag, result):
    tags = dal.get_related_tags(tag=tag)
    print(tags)
    assert tags == result
    assert len(tags) >= len(result)
    _ = None


def test_get_all_tags(dal):
    tags = dal.get_all_tags()
    print(tags)
    result = ["aaa", "bbb", "ccc", "vimania", "yyy"]
    assert tags == result
    assert len(tags) >= len(result)


@pytest.mark.parametrize(
    ("todo_id", "depth", "result_id"),
    (
        (9, -3, 3),
        (9, -2, 6),
        (9, -1, 8),
        (9, 0, 9),
        (1, 0, 1),
    ),
)
def test_get_todo_parent(dal, todo_id, depth, result_id):
    todo = dal.get_todo_parent(todo_id, depth)
    _ = None
    assert todo.id == result_id


@pytest.mark.parametrize(
    ("todo_id", "depth"),
    ((9, -3),),
)
def test_get_depth(dal, todo_id, depth):
    result = dal.get_depth(todo_id)
    _ = None
    assert result == depth


@pytest.mark.parametrize(
    ("todo_id", "overall_status"),
    (
        (3, 1),
        (11, 4),
        (12, None),
        (999999, None),
    ),
)
def test_get_overall_status(dal, todo_id, overall_status):
    result = dal.get_overall_status(todo_id)
    _ = None
    assert result == overall_status
