from pathlib import Path
import datetime
import qrun_to_pandas as qtp

sample_path = Path(__file__).parent.parent / "sample_data"


def test_version_is_correct():
    from pathlib import Path

    q = f'version = "{qtp.__version__}"'
    pyproject_toml = Path(__file__).parent.parent / "pyproject.toml"
    assert q in pyproject_toml.read_text()


def test_start_date():
    dates = qtp.extract_run_dates(sample_path / "05-07-24_RPL27.Qrun")
    assert len(dates) == 2
    assert dates[0].date() == datetime.date(2024, 5, 7)
    assert dates[0].replace(tzinfo=None) - datetime.datetime(2024, 5, 7, 14, 27, 42)< datetime.timedelta(seconds=1)
    assert dates[1].date() == datetime.date(2024, 5, 7)
    assert dates[0].replace(tzinfo=None) - datetime.datetime(2024, 5, 7, 15, 26, 23)< datetime.timedelta(seconds=1)


def test_full():
    run = qtp.extract_annotated(sample_path / "05-07-24_RPL27.Qrun")

    assert "melt_curve" in run
    mc = run["melt_curve"]
    assert len(mc["Well"].unique()) == 48
    assert mc.iloc[0]["Green"] == 64.619086
    assert mc.iloc[0]["Temperature (C)"] == 60.01
    assert mc.iloc[0]["Well"] == "1"
    assert mc.iloc[0]["Color"] == "721f7b"
    assert mc.iloc[0]["AssayName"] == "HouseKeeper38 Thermo short"
    assert mc.iloc[0]["AssayTargets"] == "HouseKeeper38"
    assert mc.iloc[-1]["Green"] == 2.299999
    assert mc.iloc[-1]["Temperature (C)"] == 93.9
    assert mc.iloc[-1]["Well"] == "48"
    assert mc.iloc[-1]["Color"] == "523e13"
    assert mc.iloc[-1]["AssayName"] == "HouseKeeper38 Thermo short"
    assert mc.iloc[-1]["AssayTargets"] == "HouseKeeper38"


    ampc = run['amplification_curve']
    assert ampc.iloc[0]["Cycle"] == 1
    assert ampc.iloc[0]["Green"] == 1.540405
    assert ampc["Cycle"].max() == 40
    assert ampc.iloc[0]["Well"] == "1"
    assert ampc.iloc[0]["Name"] == "Ctrl"
    assert ampc.iloc[0]["Color"] == mc.iloc[0]["Color"]
    assert ampc.iloc[0]["AssayName"] == mc.iloc[0]["AssayName"]
    assert ampc.iloc[0]["AssayTargets"] == mc.iloc[0]["AssayTargets"]

    xmpc = ampc[(ampc.Well == "1") & (ampc.Cycle == 40)]
    assert xmpc.iloc[0].Green == 12.037755
    assert ampc.iloc[-1].Green == 9.439371
    

    assert run['start_date'].replace(tzinfo=None) - datetime.datetime(2024, 5, 7, 14, 27, 42)< datetime.timedelta(seconds=1)
    assert run['end_date'].replace(tzinfo=None) - datetime.datetime(2024, 5, 7, 15, 26, 23)< datetime.timedelta(seconds=1)

    print(ampc.head(1).transpose())
    aoeu


