import json
from apf.consumers import KafkaConsumer
from correction_step.step import CorrectionStep


def test_step_initialization(kafka_service, env_variables):
    from scripts.run_step import step_creator

    assert isinstance(step_creator(), CorrectionStep)


def test_result_has_everything(
    kafka_service, env_variables, kafka_consumer: KafkaConsumer
):
    from scripts.run_step import step_creator

    step_creator().start()
    for message in kafka_consumer.consume():
        assert_result_has_correction_fields(message)
        kafka_consumer.commit()


def assert_result_has_correction_fields(message):
    fields = ["mag_corr", "e_mag_corr", "e_mag_corr_ext", "has_stamp"]
    assert "detections" in message
    assert all(all(f in det for f in fields) for det in message["detections"])


def test_scribe_has_detections(kafka_service, env_variables, scribe_consumer):
    from scripts.run_step import step_creator

    step = step_creator()
    step.start()

    for message in scribe_consumer.consume():
        assert_scribe_has_detections(message)
        scribe_consumer.commit()


def assert_scribe_has_detections(message):
    data = json.loads(message["payload"])
    assert "collection" in data and data["collection"] == "detection"
    assert "type" in data and data["type"] == "update"
    assert "criteria" in data and "_id" in data["criteria"]
    assert "data" in data and len(data["data"]) > 0
    assert "options" in data and "upsert" in data["options"] and "set_on_insert" in data["options"]
    assert data["options"]["upsert"] is True
    assert "has_stamp" in data["data"]
    assert "candid" not in data["data"]  # Prevent duplication with _id
    if data["data"]["has_stamp"]:
        assert data["options"]["set_on_insert"] is False
    else:
        assert data["options"]["set_on_insert"] is True


def test_works_with_batch(kafka_service, env_variables, kafka_consumer: KafkaConsumer):
    from scripts.run_step import step_creator
    import os

    os.environ["CONSUME_MESSAGES"] = "10"
    step_creator().start()

    for message in kafka_consumer.consume():
        assert_result_has_correction_fields(message)
        kafka_consumer.commit()