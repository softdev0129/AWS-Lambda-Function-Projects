from enum import Enum

class EventAction(Enum):
    START_JOB = 'start_job'
    COMPLETE_JOB = 'complete_job'
    FAIL_JOB = 'fail_job'