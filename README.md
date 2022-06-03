# Battery Estimation Project

## How to Start

To initialize repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

## To use batt-testing.py

Provide 2 ULog files, one representing a 1C drain test, another representing a 30A hover test

Prints 2 sets of 4 coefficients representing the fit curves for battery estimation

```bash
# python3 batt-testing.py <1C ULog> <30A ULog>
python3 tools/batt-testing.py data/reference_1c.ulog data/reference_30a.ulog
```
