import uuid
import threading
from concurrent.futures import ThreadPoolExecutor

class TaskManager:
    def __init__(self, max_workers=5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = {}
        self.lock = threading.Lock()

    def submit_task(self, app, func, *args, **kwargs):
        """
        Submit a background task. 
        Requires the Flask app object to push the app context.
        """
        task_id = str(uuid.uuid4())
        
        with self.lock:
            self.tasks[task_id] = {
                'status': 'pending',
                'result': None,
                'error': None
            }
            
        def task_wrapper():
            with app.app_context():
                with self.lock:
                    self.tasks[task_id]['status'] = 'running'
                try:
                    result = func(*args, **kwargs)
                    with self.lock:
                        self.tasks[task_id]['status'] = 'completed'
                        self.tasks[task_id]['result'] = result
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    with self.lock:
                        self.tasks[task_id]['status'] = 'failed'
                        self.tasks[task_id]['error'] = str(e)
                        
        self.executor.submit(task_wrapper)
        return task_id

    def get_task_status(self, task_id):
        """
        Get the status of a background task.
        """
        with self.lock:
            return self.tasks.get(task_id)

# Global task manager instance
task_manager = TaskManager()
