-- name: load_testdata!
insert into main.vimania_todos (parent_id, todo, metadata, tags, "desc", path, flags)
values (null, 'todo 1', 'TEST: entry for bookmark xxxxx', ',ccc,vimania,yyy,', 'nice description b', "filepath", 1),
       (null, 'todo 2', 'TEST: entry for bookmark bbbb', ',aaa,bbb,', 'nice description a', "filepath", 0),
       (null, 'todo 3', 'bla blub', ',aaa,bbb,', 'nice description a2', "filepath", 1),
       (3, 'todo 4', 'bla blub2', ',aaa,bbb,ccc,', 'nice description a3', "filepath", 1),
       (3, 'todo 5 inconsistency', 'blub3', ',aaa,bbb,ccc,', 'nice description a4', "filepath", 1),
       (3, 'todo 5 inconsistency', 'blub3', ',aaa,bbb,ccc,', 'INCONSISTENCY!!!!!, active at the same time', "filepath", 1),
       (6, 'todo 6', 'uniq test: allow same todos but not active at same time', ',,', '', "filepath", 4),
       (6, 'todo 6', 'uniq test: allow same todos but not active at same time', ',,', '', "filepath", 1),
       (8, 'todo 7', '', ',,', '', "filepath", 1),
       (3, 'todo 8', '', ',,', '', "filepath", 1),
       (null, 'todo 9', '', ',,', '', "filepath", 0),
       (11, 'todo 10', '', ',,', '', "filepath", 4)
       ;

