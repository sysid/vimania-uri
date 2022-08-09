select *
from vimania_todos
where todo == 'todo 10'
;

with recursive tds_children as (
    select id, parent_id, todo, 1 as depth
    from vimania_todos
    where id == 3
      and flags <= 4
    union all
    select vimania_todos.id, vimania_todos.parent_id, vimania_todos.todo, tds_children.depth + 1
    from vimania_todos
             join tds_children
    where vimania_todos.parent_id == tds_children.id
      and vimania_todos.flags < 4
)
select *
from tds_children
-- where depth = 0
;

with recursive tds_parents as (
    select id, parent_id, todo, 0 as depth
    from vimania_todos
    where id = 3
      and flags <= 4
    union all
    select vimania_todos.id, vimania_todos.parent_id, vimania_todos.todo, tds_parents.depth - 1
    from vimania_todos
             join tds_parents
    where vimania_todos.id == tds_parents.parent_id
      and vimania_todos.flags < 4
)
select *
from tds_parents
order by depth
-- limit 1
--where level < 3  -- only one level up
;

with recursive tds_parents as (
    select id,
           parent_id,
           todo,
           metadata,
           tags,
           desc,
           path,
           flags,
           last_update_ts,
           created_at,
           0 as depth
    from vimania_todos
    where todo = 'this is a text describing a task2'
      and flags < 4
    union all
    select vimania_todos.id,
           vimania_todos.parent_id,
           vimania_todos.todo,
           vimania_todos.metadata,
           vimania_todos.tags,
           vimania_todos.desc,
           vimania_todos.path,
           vimania_todos.flags,
           vimania_todos.last_update_ts,
           vimania_todos.created_at,
           tds_parents.depth - 1
    from vimania_todos
             join tds_parents
    where vimania_todos.id == tds_parents.parent_id
      and vimania_todos.flags < 4
)
select *
from tds_parents
-- where depth = 0
;

-- get depth
with recursive tds_parents as (
    select id, parent_id, todo, 0 as depth
    from vimania_todos
    where todo == 'this is a text describing a task2'
      and flags <= 4
    union all
    select vimania_todos.id, vimania_todos.parent_id, vimania_todos.todo, tds_parents.depth - 1
    from vimania_todos
             join tds_parents
    where vimania_todos.id == tds_parents.parent_id
      and vimania_todos.flags < 4
)
select *
from tds_parents
-- order by depth
-- limit 1
;

select * from vimania_todos
where todo = 'this is a text describing a task2'
