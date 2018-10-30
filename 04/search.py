import sys
import json
from scorelib.sqlite import get_print

if len(sys.argv) < 2:
    exit("Too less arguments calling script")

name = sys.argv[1]
prints = get_print(name)
print(len(prints))
print(json.dumps(prints, default=lambda x: x.format_json(), sort_keys=False, indent=2, ensure_ascii=False))