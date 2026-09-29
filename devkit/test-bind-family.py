"""Source regression check only; live socket checks are still required.

HTTP is outside this patch and must remain disabled for the private VNC setup.
"""
from pathlib import Path
import re

source = (Path(__file__).resolve().parents[1] / "src/trollvncserver.mm").read_text(encoding="utf-8")
start = source.index("static void setupRfbScreen(")
function = source[start:source.index("static void setupRfbEventHandlers", start)]
defaults, branches = function.split("TVBindHostKind hostKind =", 1)
assert "gScreen->port = gPort;" in defaults
assert "gScreen->ipv6port = gPort;" in defaults
v4 = branches.split("if (hostKind == kTVBindHostKindIPv4) {", 1)[1].split("} else if", 1)[0]
v6 = branches.split("} else if (hostKind == kTVBindHostKindIPv6) {", 1)[1].split("} else if", 1)[0]
assert "gScreen->ipv6port = 0;" in v4 and "gScreen->port = 0;" not in v4
assert "gScreen->port = 0;" in v6 and "gScreen->ipv6port = 0;" not in v6
tail = branches.split("} else if (hostKind == kTVBindHostKindInvalid", 1)[1]
assert not re.search(r"gScreen->(?:ipv6)?port\s*=\s*0\s*;", tail)
print("PASS: explicit VNC bind disables the other address family; defaults preserved")
