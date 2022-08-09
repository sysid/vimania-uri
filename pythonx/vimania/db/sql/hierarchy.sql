-- name: get_overall_status
with recursive tds_children as (
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
    where id == :id_
      and flags <= 4
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
           tds_children.depth + 1
    from vimania_todos
             join tds_children
    where vimania_todos.parent_id == tds_children.id
      and vimania_todos.flags <= 4
)
select min(flags) overall_status
from tds_children
where id != :id_
--where level < 3  -- only one level down
;

-- name: get_todo_parent
-- record_class: Todo
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
    where id = :id_
      and flags <= 4
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
      and vimania_todos.flags <= 4
)
select *
from tds_parents
where depth = :depth
;


-- name: get_depth
with recursive tds_parents as (
    select id, parent_id, todo, 0 as depth
    from vimania_todos
    where id == :id_
      and flags <= 4
    union all
    select vimania_todos.id, vimania_todos.parent_id, vimania_todos.todo, tds_parents.depth - 1
    from vimania_todos
             join tds_parents
    where vimania_todos.id == tds_parents.parent_id
      and vimania_todos.flags < 4
)
select depth
from tds_parents
order by depth
limit 1
;

