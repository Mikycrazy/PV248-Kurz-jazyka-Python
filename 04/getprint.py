import sys
import json
from scorelib.sqlite import get_composers

if len(sys.argv) < 2:
    exit("Too less arguments calling script")

print_id = int(sys.argv[1])
composers = get_composers(print_id)
print(json.dumps(composers, default=lambda x: x.format_json(), sort_keys=True, indent=4))
