# Generate a profile for [YABFC](https://github.com/yabfc/yabfc) from a Factorio dump

This script generates a profile that can be used in [YABFC](https://github.com/yabfc/yabfc) from a Factorio dump

## Prerequisites

- python 3.11+ or `uv` if preferred

## Generate the dump

To create the required data dump, start Factorio with the `--dump-data` flag

### Option 1: Steam

1. Open Steam.
2. Right-click **Factorio** -> **Properties**
3. Add the following to **Launch Options**: `--dump-data`
4. Start the game

Factorio will launch, generate the dump, and then close automatically. Don't forget to remove the Launch option afterwards.

### Option 2: Run the Binary Directly

From a terminal:

```bash
factorio --dump-data
```

### Locate the generated dump

After running with `--dump-data`, the file will be created in:

**Linux**:

```
~/.factorio/script-output
```

**Windows**:

```
%appdata%/Factorio/script-output
```

Copy the `data-raw-dump.json` into this project directory, or provide the full path when running the script.

## Run the Script

Using `uv`:

```bash
uv run main.py -i data-raw-dump.json
```

Or with python directly

```bash
python3 main.py -i data-raw-dump.json
```

The script will dump the generated profile in the current working directory in the file `profile.json` if no other output is specified.

### Example help output

```
usage: main.py [-h] -i INPUT [-o OUTPUT] [-a]

YABFC Profile Generator for Factorio dumps

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
  -o OUTPUT, --output OUTPUT  (defaults to profile.json)
  -a, --auto-fix        Automatically add missing items / recipes as dummy
```

## Contributing

If you find a bug, feel free to open an issue.
