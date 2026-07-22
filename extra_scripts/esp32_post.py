#!/usr/bin/env python3
# trunk-ignore-all(ruff/F821)
# trunk-ignore-all(flake8/F821): For SConstruct imports
import shlex
from pathlib import Path

from SCons.Script import COMMAND_LINE_TARGETS

Import("env")


def cleanup_framework_partitions(target, source, env):
    framework_dir = env.PioPlatform().get_package_dir("framework-arduinoespressif32")
    partitions_dir = Path(framework_dir) / "tools" / "partitions"
    patched = partitions_dir / "patched"

    # After the project build ends, restore the framwork partition .csv files
    # so using this framework with other projects won't affect the user experience
    # it will only run if it had been successfully patched before.
    if not patched.exists():
        return
    env.Execute(f"sed -i 's/mesht/spiffs/' {shlex.quote(str(partitions_dir))}/*.csv")
    patched.unlink()


# For a normal build, the cleanup runs after buildprog. For pio `run -t mtjson`,
# it runs after `mtjson`, preventing cleanup too early before the manifest reads
# the patched partition table.
cleanup_target = "mtjson" if "mtjson" in COMMAND_LINE_TARGETS else "buildprog"
env.AddPostAction(cleanup_target, cleanup_framework_partitions)
