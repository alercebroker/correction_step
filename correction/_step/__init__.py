from .step import CorrectionStep
import os
import pyroscope


def run_step():
    if bool(os.getenv("USE_PROFILING", True)):
        pyroscope.configure(application_name="steps.correction", server_address=os.getenv("PYROSCOPE_SERVER"))

        with pyroscope.tag_wrapper({"function": "start"}):
            CorrectionStep.create_step().start()

    else:
        CorrectionStep.create_step().start()
