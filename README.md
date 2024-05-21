# qrun-to-pandas

[![License](https://img.shields.io/github/license/TyberiusPrime/qrun-to-pandas)](https://img.shields.io/github/license/TyberiusPrime/qrun-to-pandas)

Read Quantabio QRun formated files into pandas dataframes

- **Github repository**: <https://github.com/TyberiusPrime/qrun-to-pandas/>

## Usage

```python
>> data = qrun_to_pands.extract_annotated("filename.qrun")
>> print(data.keys())
dict_keys(['melt_curve', 'amplification_curve','start_date','end_date'])

>> data['melt_curve'].head(1).transpose()
                                          0
Temperature (C)                       60.01
Green                             64.619086
Well                                      1
Name                                   Ctrl
AssayName        HouseKeeper38 Thermo short
AssayTargets                  HouseKeeper38
Color                                721f7b

>> data['amplification_curve'].head(1).transpose()
                                       0
Cycle                                  1
Green                           1.540405
Well                                   1
Name                                Ctrl
AssayName     HouseKeeper38 Thermo short
AssayTargets               HouseKeeper38
Color                             721f7b
```



