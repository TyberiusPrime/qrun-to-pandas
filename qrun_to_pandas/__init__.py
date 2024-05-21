import xml.etree.ElementTree as ET
import datetime
import collections
import pandas as pd

__version__ = "0.1.0"


def extract_sample_data(filename, fields=["Well", "Name", "Colour"]):
    """Exract the sample information"""
    tree = ET.parse(filename)
    sd = tree.find("SampleData").find("Samples").findall("Sample")

    result = collections.defaultdict(list)
    for sample in sd:
        for field in fields:
            result[field].append(sample.find(field).text)
    return pd.DataFrame(result)


def extract_time_trace(filename, trace_name):
    """Extract a TimeTrace"""
    tree = ET.parse(filename)
    traces = tree.find("RunData").find("TimeTraces").findall("Trace")
    for tt in traces:
        if tt.attrib["Name"] == trace_name:
            return parse_trace(tt.text, "Time", trace_name)
    raise KeyError("Trace not found", trace_name)


def extract_datasets(filename):
    """Extract all datasets from a qrun file"""
    result = {}
    tree = ET.parse(filename)
    datasets = tree.find("RunData").find("DataSets").findall("DataSet")
    for ds in datasets:
        name = ds.find("Name").text
        kind = ds.find("Type").text
        step_id = ds.find("StepID").text
        channel = ds.find("Channel").text
        if kind == "Cycling":
            x = "Cycle"
        elif kind == "Melt":
            x = "Temperature (C)"
        else:
            x = "x (unknown)"
        traces = []
        for tr in ds.find("Traces").findall("Trace"):
            trace = parse_trace(tr.text, x, channel)
            trace = trace.assign(Well=tr.attrib["Well"])
            traces.append(trace)
        traces = pd.concat(traces)
        if kind in result:
            raise ValueError("Duplicate dataset - unexpected", kind)
        result[kind] = {"traces": traces, "step_id": step_id}
    return result


def extract_run_dates(filename):
    """Extract the run start and end dates"""
    tree = ET.parse(filename)
    start_date = tree.find("RunData").find("Start").text
    end_date = tree.find("RunData").find("End").text
    return datetime.datetime.fromisoformat(start_date), datetime.datetime.fromisoformat(
        end_date
    )


def extract_assays(filename):
    """Retrieve all the assys included in the qrun file""" 
    tree = ET.parse(filename)
    assays = tree.find("Assays").findall("Assay")
    res = collections.defaultdict(list)
    for assay in assays:
        res["Name"].append(assay.find("Name").text)
        res["ID"].append(assay.find("ID").text)
        res["StepIDs"].append(
            " ".join([x.find("ID").text for x in assay.findall("Profile/Steps/Step")])
        )
        res["Targets"].append(
            " ".join(x.find("Name").text for x in assay.findall("Targets/Target"))
        )
    return pd.DataFrame(res).set_index("ID")


def parse_trace(input: str, column_name_x: str, column_name_y: str):
    """Parse the data from the traces format (x:y tuples seperated by spaces)
    into a dataframe with the given column names"""
    res = {"x": [], "y": []}
    for element in input.split():
        x, y = element.split(":")
        res["x"].append(float(x))
        res["y"].append(float(y))
    res = pd.DataFrame(res)
    res.columns = [column_name_x, column_name_y]
    return res


def build_annotated_curve(datasets, kind, sample_info, step_id_to_assay_info):
    """Anotate the datasets with AssayNam and AssayTargets"""
    curve = datasets[kind]["traces"].merge(sample_info, on="Well")
    step_id = datasets[kind]["step_id"]
    assay_info = step_id_to_assay_info[step_id]
    return curve.assign(
        AssayName=assay_info["Name"],
        AssayTargets=assay_info["Targets"],
    )


def extract_annotated(filename) -> dict[str, pd.DataFrame | datetime.datetime]:
    """High level entry point: extract the melt_curve and amplification_curve dataframes,
    as well as the run start_date end_dates

    """
    assays = extract_assays(filename)
    step_id_to_assay_info = {}
    for _idx, row in assays.iterrows():
        for x in row["StepIDs"].split():
            step_id_to_assay_info[x] = row
    datasets = extract_datasets(filename)  # thats,
    sample_info = extract_sample_data(filename)
    start_date, end_date = extract_run_dates(filename)

    melt_curve = build_annotated_curve(
        datasets, "Melt", sample_info, step_id_to_assay_info
    )
    melt_curve = melt_curve.assign(Color = melt_curve['Colour']).drop(columns=['Colour'])
    amp_curve = build_annotated_curve(
        datasets, "Cycling", sample_info, step_id_to_assay_info
    )
    amp_curve = amp_curve.assign(Cycle = amp_curve['Cycle'].astype(int) + 1)
    amp_curve = amp_curve.assign(Color = amp_curve['Colour']).drop(columns=['Colour'])

    return {
        "melt_curve": melt_curve,
        "amplification_curve": amp_curve,
        "start_date": start_date,
        "end_date": end_date,
    }
