import functools
import logging

import pghistory
from django.db import close_old_connections
from django.db import reset_queries
from procrastinate import JobContext
from procrastinate.contrib.django import app

logger = logging.getLogger(__name__)


def define_task(original_func=None, **kwargs):
    """
    A wrapper around @app.task that adds pghistory context to the task execution.

    Any database changes that happen during the task execution will be correlatable.

    This is leveraging a technique from https://github.com/procrastinate-org/procrastinate/issues/1316
    that purports to resolve our too-many-database-connection issue. It seems that procrastinate
    and django together have issues closing their connections.
    """

    # we always needs `pass_context=True` to get the JobContext,
    # but the wrapped function may not want it.
    pass_context_to_func = kwargs.pop("pass_context", False)

    def decorator(func):
        @functools.wraps(func)
        def new_func(context: JobContext, *job_args, **job_kwargs):
            close_old_connections()
            reset_queries()
            try:
                with pghistory.context(job=context.job.id, task_name=context.job.task_name):
                    if pass_context_to_func:
                        result = func(context, *job_args, **job_kwargs)
                    else:
                        result = func(*job_args, **job_kwargs)
                    return result
            finally:
                close_old_connections()
                reset_queries()

        kwargs["pass_context"] = True
        return app.task(**kwargs)(new_func)

    if original_func:
        return decorator(original_func)

    return decorator
