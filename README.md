# Battery Estimation Project

![workflow](https://github.com/tonysamaritano/ulog-battery-est/actions/workflows/batlib.yaml/badge.svg)
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
# python3 batt-testing.py -o <1C ULog> -t <30A ULog> -c <Capacity>
python3 tools/batt-testing.py -o data/reference_1c.ulog -t data/reference_30a.ulog
```

## Simple analysis

```bash
python3 tools/BatteryModelDriver.py 12.0
```