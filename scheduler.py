from Queue import Queue

class Task(object):
    taskid = 0
    def __init__(self,target):
        Task.taskid += 1
        self.tid = Task.taskid
        self.target = target
        self.sendval = None
    def run(self):
        return self.target.send(self.sendval)

class SystemCall(object):
    def handle(self):
        pass

class GetTid(SystemCall):
    def handle(self):
        self.task.sendval = self.task.tid
        self.sched.schedule(self.task)

class NewTask(SystemCall):
    def __init__(self, target):
        self.target = target
    def handle(self):
        tid = self.sched.new(self.target)
        self.task.sendval = tid
        self.sched.schedule(self.task)

class KillTask(SystemCall):
    def __init__(self, tid):
        self.tid = tid

    def handle(self):
        task = self.sched.taskmap.get(self.tid, None)
        if task:
            task.target.close()
            self.task.sendval = True
        else:
            self.task.sendval = False
        self.sched.schedule(self.task)

class WaitTask(SystemCall):
    def __init__(self, tid):
        self.tid = tid

    def handle(self):
        result = self.sched.waitforexit(self.task, self.tid)
        self.task.sendval = result
        if not result:
            self.sched.schedule(self.task)

class Scheduler(object):
    def __init__(self):
        self.ready = Queue()
        self.taskmap = {}
        self.exit_waiting = {}

    def exit(self,task):
        print "Task terminated %s " % task.tid
        del self.taskmap[task.tid]
        # Notify other tasks waiting for exit
        for task in self.exit_waiting.pop(task.tid, []):
            self.schedule(task)

    def waitforexit(self, task, waittid):
        if waittid in self.taskmap:
            self.exit_waiting.setdefault(waittid, []).append(task)
            return True
        else:
            return False

    def new(self, target):
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        print "Created task with id %s " % newtask.tid
        return newtask.tid

    def schedule(self, task):
        self.ready.put(task)

    def mainloop(self):
        while self.taskmap:
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    result.task = task
                    result.sched = self
                    result.handle()
                    continue
            except StopIteration,e:
                self.exit(task)
                continue
            self.schedule(task)

# def foo():
#     mytid = yield GetTid()
#     for i in xrange(10):
#        print "I'm foo with taskid ", mytid
#        yield
        
# def bar():
#     mytid = yield GetTid()
#     for i in xrange(5):
#         print "I'm bar with taskid", mytid
#         yield

# sched = Scheduler()
# sched.new(foo())
# sched.new(bar())
# sched.mainloop()

# def foo():
#     mytid = yield GetTid()
#     while True:
#         print "I'm foo ", mytid
#         yield

# def main():
#     child = yield NewTask(foo())
#     for i in xrange(5):
#         yield
#     yield KillTask(child)
#     print "Main done "

def handle_client(client,addr):
    print "Connection from ", addr
    while True:
        data = client.recv(65536)
        if not data:
            break
        client.send(data)
    client.close()
    print "Client closed "
    yield

def server(port):
    print "Server starting "
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(("",port))
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        yield NewTask(handle_client(client,addr))

def foo():
    for i in xrange(5):
        print "I;m foo"
        yield

def main():
    child = yield NewTask(foo())
    print "Waiting for child "
    yield WaitTask(child)
    print "Child one"

sched = Scheduler()
sched.new(main())
sched.mainloop()
