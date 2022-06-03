# Battery Estimation Project

## How to Start

To initialize repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

## Test

To run a simple test script, run this:

```bash
# python3 tools/pyulog-test.py <path to ulog>.ulg
python3 tools/pyulog-test.py data/21_27_56.ulog
```

## To use batt-testing.py
Provide 2 ULog files, one representing a 1C drain test, another representing a 30A hover test

Returns 2 sets of 4 coefficients representing the fit curves for battery estimation

```py batt-testing.py <1C ULog> <30A ULog>```
