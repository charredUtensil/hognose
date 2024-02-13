# Changing the major version number means:
#   No attempt has been made to have a seed generate the same cavern it did
#   before. The layout has completely changed.
# (Version 0 makes no promises about this, though.)
MAJOR    = 0

# Changing the minor version number means:
#   There is some significant gameplay difference between this and a previous
#   cavern. Perhaps there's a new planner available, or the position of a
#   lake has changed.
MINOR    = 6

# Changing the revision number means:
#   A generated cavern will have almost identical gameplay as before. Maybe
#   some crystals are in slightly different places, or landslides happen more
#   or less frequently, or there are small variations in the shape of rooms
#   i.e. there are three monsters now instead of four.
REVISION = 7

# Suffix indicating the type of build.
#   no suffix: stable
#   x: experimental
SUFFIX   = ''

VERSION_INFO = (MAJOR, MINOR, REVISION)
VERSION = f'{MAJOR:d}.{MINOR:02d}.{REVISION:02d}{SUFFIX}'