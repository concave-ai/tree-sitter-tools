from pathlib import Path

from parser.parser import parse_code
from printer import print_result, print_code_block
from scan import DirPackageScanner

p = "/Users/justwph/labs/hackathons/2024/libs/django"
scanner = DirPackageScanner(
    Path(p))
scanner.scan()


# for i in scanner.files:
#     res = parse_code(i["path"])
#     print(res["time_used_ms"], res["path"])
#     print(res["funcs"])
#     print("=====================================")

result = parse_code(Path("/Users/justwph/labs/hackathons/2024/libs/django/django/apps/config.py"), "django.apps.config")
# print_result(result)
print_code_block(result)