from __future__ import absolute_import

from celery import Celery

celery = Celery('tasks.celery',
                broker='amqp://',
                backend='amqp://',
                include=['tasks.read_update_feed'])

# Optional configuration, see the application user guide.
celery.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    celery.start()
