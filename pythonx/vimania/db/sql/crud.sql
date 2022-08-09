/*
Gotcha:
    returning is not working here but inline. Strange!!!
 */

-- name: insert_todo<!
-- returning not working here, but in query inline (see code)
insert into vimania_todos (parent_id, todo, metadata, tags, desc, path, flags, created_at)
values (:parent_id, :todo, :metadata, :tags, :desc, :path, :flags, :created_at)
--  returning *
;

-- name: get_todo_by_id^
select *
from vimania_todos
where id = :id
;

-- name: get_related_tags
--- :tag_query '%,ccc%'
-- result-title: related-tags
with RECURSIVE split(tags, rest) AS (
    SELECT '', tags || ','
    FROM vimania_todos
    WHERE tags LIKE :tag_query
          -- WHERE tags LIKE '%,ccc,%'
    UNION ALL
    SELECT substr(rest, 0, instr(rest, ',')),
           substr(rest, instr(rest, ',') + 1)
    FROM split
    WHERE rest <> '')
SELECT distinct tags
FROM split
WHERE tags <> ''
ORDER BY tags;

-- name: get_all_tags
-- result-title: tags
with RECURSIVE split(tags, rest) AS (
    SELECT '', tags || ','
    FROM vimania_todos
    UNION ALL
    SELECT substr(rest, 0, instr(rest, ',')),
           substr(rest, instr(rest, ',') + 1)
    FROM split
    WHERE rest <> '')
SELECT distinct tags
FROM split
WHERE tags <> ''
ORDER BY tags;
