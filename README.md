# SMONI - Scope Monitor

Be always aware of any updates on bug bounty programs you hunt.

## Features
- Download scope from a single program independently using the `-s` option.

## Current Supported Platforms
- HackerOne

## Usage
### Getting results from a single program
You must specify the platform to which the program belongs.

Use syntax -> `platform:program`
- `h1` for HackerOne

#### Example:
```python
python3 smoni.py -s h1:netflix # This will return active and bounty eligible URLs 
```

You can also use `--scope`

### Saving Results

You can also save an entire `.csv` file on current directory by just passing the option `--csv`
