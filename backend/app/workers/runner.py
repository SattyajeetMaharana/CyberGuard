from .contracts import WorkerJob


def run_job(job: WorkerJob):
    return job.handler()