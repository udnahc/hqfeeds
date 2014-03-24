source python2.6.9/bin/activate

celery -A tasks worker --loglevel=info

export APP_CONFIG=dev.cfg

from tasks import task_invoker

task_invoker.create_entries()

task_invoker.parse_feed()
