# https://regex101.com/
import re

################################################################################
# URL
################################################################################
# pattern = re.compile(r""".*vm::(.*)\)+""")
from enum import IntEnum

URL_PATTERN = re.compile(
    r""".*(https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b[-a-zA-Z0-9@:%_\+.~#?&\/=]*)"""
)

################################################################################
# TODO_PATTERN
#
# vim: https://marcelfischer.eu/blog/2019/checkbox-regex/
# string.match(/\[[^\]]*\]\([^)]*\)*/)
# (?:__|[*#])|\[(.+?)]\((.+?)\)

# "\[([ \-xX]{1})\] ([\d\w\s]+)"gm

# markdownlink: "^\[([\w\s\d]+)\]\((https?:\/\/[\w\d./?=#]+)\)$"gm: https://regex101.com/r/m9dndl/1
# /* Match only links that are fully qualified with https */
# const fullLinkOnlyRegex = /^\[([\w\s\d]+)\]\((https?:\/\/[\w\d./?=#]+)\)$/
# /* Match full links and relative paths */
# const regex = /^\[([\w\s\d]+)\]\(((?:\/|https?:\/\/)[\w\d./?=#]+)\)$/
# vim regex: https://marcelfischer.eu/blog/2019/checkbox-regex/
################################################################################

r"""
"^(\t*)(\s*[-*]\s?)(%\d+%)?(.?)(\[[ \-xXdD]{1}])( )([^{}]+?)({t:.+})?$"gmx

- [ ] bla bub ()
   - [ ] bla bub ()
	- [ ] bla bub2 ()
		- [ ] bla bub3 ()
- [b] xxxx: invalid
[ ] xxxx: invalid
    - [ ] todoa ends () hiere.
- vimaniax: invalid
- [x] this is a text describing a task
- [x] this is a text describing a task %%123%%
- %123% [x] this is a text describing a task
- %123% [d] should be deleted
- [D] should be deleted
- %9% [d] this is a text for deletion {t:todo,py}
"""

# TODO_PATTERN = re.compile(
#     r"""^(\t*)(\s*[-*]\s?)(%\d+%)?(.?)(\[[ \-xXdD]{1}])( )([^{}]+?)({t:.+})?$"""
# )
TODO_PATTERN = re.compile(
    r"""
^
  (\t*)                 # 1 tab indentation (hierarchy)
  (\s*[-*]\s?)          # 2 -/* todo marker
  (%\d+%)?              # 3 hidden SQL id
  (.?)                  # 4
  (\[[ \-xXdD]{1}])     # 5 [ ] status
  (\s+)                 # 6 space before todo (mandatory)
  ([^{}]+?)             # 7 minimal todo string until {}
  ({t:.+})?             # 8 optional tag
$
""",
    re.VERBOSE,
)


class MatchEnum(IntEnum):
    """Group number of Match object"""

    ALL = 0
    LEVEL = 1  # tab group
    FILL0 = 2  # -.
    CODE = 3  # %123%
    FILL1 = 4  # blank
    STATUS = 5  # [x]
    FILL2 = 6  # blanks
    TODO = 7  # text
    TAGS = 8  # {t:todo,py}
