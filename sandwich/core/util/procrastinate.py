import functools

import pghistory
from procrastinate import JobContext
from procrastinate.contrib.django import app


def define_task(original_func=None, **kwargs):
    """
    A wrapper around @app.task that adds pghistory context to the task execution.

    Any database changes that happen during the task execution will be correlatable.
    """

    # we always needs `pass_context=True` to get the JobContext,
    # but the wrapped function may not want it.
    pass_context_to_func = kwargs.pop("pass_context", False)

    def decorator(func):
        @functools.wraps(func)
        def new_func(context: JobContext, *job_args, **job_kwargs):
            with pghistory.context(job=context.job.id, task_name=context.job.task_name):
                if pass_context_to_func:
                    result = func(context, *job_args, **job_kwargs)
                else:
                    result = func(*job_args, **job_kwargs)
                return result

        kwargs["pass_context"] = True
        return app.task(**kwargs)(new_func)

    if original_func:
        return decorator(original_func)

    return decorator
