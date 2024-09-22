from threading import Thread
from multiprocessing import Process


running_threads = dict()
running_processes = dict()


def multi_thread(thread_list_identifier):
    print(f'Running a new thread with identifier: {thread_list_identifier}')
    def decorator(function):
        def wrapper(*args, **kwargs):
            global running_processes
            if thread_list_identifier not in running_threads:
                running_threads[thread_list_identifier] = list()
                
            thread = Thread(target=function, args=args, kwargs=kwargs)
            thread.setDaemon(True)
            thread.start()
            running_threads[thread_list_identifier].append(thread)
        return wrapper
    return decorator


def multi_process(process_list_identifier):
    print(f'Running a new process with identifier: {process_list_identifier}')
    def decorator(function):
        def wrapper(*args, **kwargs):
            global running_processes
            if process_list_identifier not in running_processes:
                running_processes[process_list_identifier] = list()
            process = Process(target=function, args=tuple(args), kwargs=kwargs)
            process.start()
            running_processes[process_list_identifier].append(process)
        return wrapper
    return decorator