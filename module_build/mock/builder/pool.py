from multiprocessing import Process, Queue


class MockBuildPool(object):
    def __init__(self, queue_processes, *args, **kwargs):
        self.queue = Queue()
        self.processes = []

        self.init_processes(queue_processes)

    def init_processes(self, queue_processes):
        for i in range(queue_processes):
            p = Process(target=self.make_pool_call)
            p.start()
            self.processes.append(p)
