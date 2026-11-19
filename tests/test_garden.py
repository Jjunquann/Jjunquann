from datetime import date
from generators.garden import season_of, render
assert season_of(date(2025, 12, 5)) == (2026, "winter")
assert season_of(date(2025, 3, 1)) == (2025, "spring")
assert season_of(date(2025, 11, 30)) == (2025, "autumn")
assert render("x", 2025, {(2025, "spring"): 5}).count("class=\"sw\"") == 1
