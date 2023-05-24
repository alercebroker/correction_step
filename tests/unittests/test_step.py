import copy
import json
from copy import deepcopy
from unittest import mock

from correction._step import CorrectionStep

from tests.utils import ztf_alert, atlas_alert, non_detection

messages = [
    {
        "aid": "AID1",
        "detections": [ztf_alert(candid="a", new=True), ztf_alert(candid="b", has_stamp=False, new=False, forced=True)],
        "non_detections": [],
    },
    {
        "aid": "AID2",
        "detections": [ztf_alert(aid="AID2", candid="c", new=True), ztf_alert(aid="AID2", candid="d", has_stamp=False, new=True)],
        "non_detections": [non_detection(aid="AID2", mjd=1, oid="oid1", fid=1)],
    },
    {"aid": "AID3", "detections": [atlas_alert(aid="AID3", candid="e", new=True)], "non_detections": []},
]

message4produce = [
    {
        "aid": "AID1",
        "meanra": 1,
        "meandec": 1,
        "detections": [ztf_alert(candid="a", new=True), ztf_alert(candid="b", has_stamp=False, forced=True, new=False)],
        "non_detections": [],
    },
    {
        "aid": "AID2",
        "meanra": 1,
        "meandec": 1,
        "detections": [ztf_alert(aid="AID2", candid="c", new=True), ztf_alert(aid="AID2", candid="d", has_stamp=False, new=True)],
        "non_detections": [non_detection(aid="AID2", mjd=1, oid="oid1", fid=1)],
    },
    {
        "aid": "AID3",
        "meanra": 1,
        "meandec": 1,
        "detections": [atlas_alert(aid="AID3", candid="e", new=True)],
        "non_detections": [],
    },
]

message4execute = {
    "detections": [
        ztf_alert(aid="AID1", candid="a", new=True),
        ztf_alert(aid="AID1", candid="b", has_stamp=False, new=False, forced=True),
        ztf_alert(aid="AID2", candid="c", new=True),
        ztf_alert(aid="AID2", candid="d", has_stamp=False, new=True),
        atlas_alert(aid="AID3", candid="e", new=True),
    ],
    "non_detections": [
        non_detection(aid="AID2", mjd=1, oid="oid1", fid=1),
    ],
    "coords": {
        "AID1": {"meanra": 1, "meandec": 1},
        "AID2": {"meanra": 1, "meandec": 1},
        "AID3": {"meanra": 1, "meandec": 1},
    },
}


def test_pre_execute_formats_message_with_all_detections_and_non_detections():
    formatted = CorrectionStep.pre_execute(messages)
    assert "detections" in formatted
    assert formatted["detections"] == message4execute["detections"]
    assert "non_detections" in formatted
    assert formatted["non_detections"] == message4execute["non_detections"]


@mock.patch("correction._step.step.Corrector")
def test_execute_calls_corrector_for_detection_records_and_keeps_non_detections(mock_corrector):
    formatted = CorrectionStep.execute(message4execute)
    assert "detections" in formatted
    assert "non_detections" in formatted
    assert formatted["non_detections"] == message4execute["non_detections"]
    mock_corrector.assert_called_with(message4execute["detections"])
    mock_corrector.return_value.corrected_as_records.assert_called_once()


@mock.patch("correction._step.step.Corrector")
def test_execute_removes_duplicate_non_detections(_):
    message4execute_copy = deepcopy(message4execute)
    message4execute_copy["non_detections"] = (
        message4execute_copy["non_detections"] + message4execute_copy["non_detections"]
    )
    formatted = CorrectionStep.execute(message4execute_copy)
    assert "non_detections" in formatted
    assert formatted["non_detections"] == message4execute["non_detections"]


@mock.patch("correction._step.step.Corrector")
def test_execute_works_with_empty_non_detections(_):
    message4execute_copy = deepcopy(message4execute)
    message4execute_copy["non_detections"] = []
    formatted = CorrectionStep.execute(message4execute_copy)
    assert "non_detections" in formatted
    assert formatted["non_detections"] == []


def test_post_execute_calls_scribe_producer_for_each_detection():
    # To check the "new" flag is removed
    message4execute_copy = copy.deepcopy(message4execute)
    message4execute_copy["detections"] = [{k: v for k, v in det.items()} for det in message4execute_copy["detections"]]

    class MockCorrectionStep(CorrectionStep):
        def __init__(self):
            self.scribe_producer = mock.MagicMock()

    step = MockCorrectionStep()
    output = step.post_execute(copy.deepcopy(message4execute))
    assert output == message4execute_copy
    for det in message4execute_copy["detections"]:
        if not det["new"]:  # does not write
            continue
        data = {
            "collection": "detection" if not det["forced"] else "forced_photometry",
            "type": "update",
            "criteria": {"_id": det["candid"]},
            "data": {k: v for k, v in det.items() if k not in ["candid", "forced", "new"]},
            "options": {"upsert": True, "set_on_insert": not det["has_stamp"]},
        }
        step.scribe_producer.produce.assert_any_call({"payload": json.dumps(data)})


def test_pre_produce_unpacks_detections_and_non_detections_by_aid():
    # Input with the "new" flag is removed
    message4execute_copy = copy.deepcopy(message4execute)
    message4execute_copy["detections"] = [{k: v for k, v in det.items()} for det in message4execute_copy["detections"]]

    formatted = CorrectionStep.pre_produce(message4execute_copy)
    assert formatted == message4produce
