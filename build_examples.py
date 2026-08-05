import os
from pathlib import Path

base_dir = Path("/home/satvik/Projects/ragebaitGPT/creator_examples")

def write_file(path, content):
    p = base_dir / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

# Rainbow spiral
write_file("rainbow_spiral/manifest.toml", """\
format_version = "1"
id = "org.community.rainbow-spiral"
slug = "rainbow-spiral"
name = "Rainbow Spiral"
version = "1.0.0"
author_name = "Community"
author_handle = "community"
description = "A beautiful rainbow spiral animation."
license = "MIT"
entry_scene = "main"
minimum_width = 80
minimum_height = 24
recommended_duration_ms = 10000
supports_ascii = true
supports_monochrome = false
tags = ["spiral", "color", "math"]
""")

write_file("rainbow_spiral/src/design.py", """\
from clearfx.compiler.creator_sdk import CreatorAnimation

class RainbowSpiral(CreatorAnimation):
    def __init__(self):
        super().__init__()
        self.add_text("Rainbow Spiral", 0, 0)
        # More drawing logic would go here
""")

write_file("rainbow_spiral/README.md", "# Rainbow Spiral\n\nExample showing how to use the SDK to create a spiral.")

# Wave collapse
write_file("wave_collapse/manifest.toml", """\
format_version = "1"
id = "org.community.wave-collapse"
slug = "wave-collapse"
name = "Wave Collapse"
version = "1.0.0"
author_name = "Community"
author_handle = "community"
description = "Quantum wave function collapse visualization."
license = "MIT"
entry_scene = "main"
minimum_width = 80
minimum_height = 24
recommended_duration_ms = 5000
supports_ascii = true
supports_monochrome = true
tags = ["physics", "wave", "quantum"]
""")

write_file("wave_collapse/src/design.py", """\
from clearfx.compiler.creator_sdk import CreatorAnimation

class WaveCollapse(CreatorAnimation):
    def __init__(self):
        super().__init__()
        self.add_particles()
""")

write_file("wave_collapse/README.md", "# Wave Collapse\n\nExample showing particles.")

# Star burst
write_file("star_burst/manifest.toml", """\
format_version = "1"
id = "org.community.star-burst"
slug = "star-burst"
name = "Star Burst"
version = "1.0.0"
author_name = "Community"
author_handle = "community"
description = "Exploding star animation."
license = "MIT"
entry_scene = "main"
minimum_width = 80
minimum_height = 24
recommended_duration_ms = 3000
supports_ascii = true
supports_monochrome = true
tags = ["space", "explosion", "particles"]
""")

write_file("star_burst/src/design.py", """\
from clearfx.compiler.creator_sdk import CreatorAnimation

class StarBurst(CreatorAnimation):
    def __init__(self):
        super().__init__()
        self.add_circle(40, 12, 10)
""")

write_file("star_burst/README.md", "# Star Burst\n\nExample showing explosions.")
