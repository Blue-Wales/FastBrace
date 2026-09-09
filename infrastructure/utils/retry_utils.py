#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : retry_utils.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

import time
from collections import defaultdict
from functools import wraps

ON_RETRY = "on_retry"
ON_SUCCESS = "on_success"
ON_FAILED = "on_failed"


def retry(retry_when=None, retry_times=0, retry_interval=None, hooks=None, reraise=True):
    """重试装饰器

    用法示例：
    @retry(
        retry_when=when_exceptions_type(ZeroDivisionError, ValueError),
        retry_times=3,
        retry_interval=0.5,
        hooks={
            "on_retry": lambda args, kwargs, outcome, exception: print("on_retry..."),
            "on_failed": lambda args, kwargs, outcome, exception: print(
                f"Max retries: {exception}"
            ),
            "on_success": lambda args, kwargs, outcome, exception: print(
                f"Success: {outcome}"
            ),
        },
    )
    def division(x, y):
        return x / y

    :param retry_when: 在什么条件下重试，接收参数为被装饰函数的返回值和异常，当返回True时表示需要重试，默认None表示遇到异常则无条件重试
    :param retry_times: 重试次数，默认0，当<=0时，表示重试无限次
    :param retry_interval: 重试间隔，默认None表示无间隔
    :param hooks: 钩子，格式为：{"on_retry": <function>, "on_success": <function>, "on_failed": <function>}
        分别表示：
            on_retry：在每次重试时执行 -> func(args, kwargs, outcome, exception)
            on_success：在执行成功时执行 -> func(args, kwargs, outcome, exception)
            on_failed：在重试超出限制次数之后仍然被retry_when判定为失败时执行 -> func(args, kwargs, outcome, exception)
    :param reraise: 在重试失败之后是否再次抛出该异常，默认True
    :return:
    """
    _hooks = defaultdict(lambda: lambda *args, **kwargs: None)
    if hooks:
        _hooks.update(hooks)

    def inner(func):

        class Wrapper:
            def __init__(self, wrapped):
                self.wrapped = wrapped
                self.args = ()
                self.kwargs = ()
                self.outcome = None
                self.exception = None

            def __call__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs
                try:
                    self.outcome = self.wrapped(*args, **kwargs)
                except Exception as err:
                    self.exception = err

        @wraps(func)
        def wrapper(*args, **kwargs):
            wrapper_obj = Wrapper(func)
            cur_retry_times = 0
            while True:
                if 0 < retry_times <= cur_retry_times:
                    # 到达最大次数
                    _hooks[ON_FAILED](args, kwargs, wrapper_obj.outcome, wrapper_obj.exception)
                    if reraise:
                        raise wrapper_obj.exception
                    return None

                wrapper_obj(*args, **kwargs)
                if retry_when(args, kwargs, wrapper_obj.outcome, wrapper_obj.exception):
                    if retry_interval:
                        time.sleep(retry_interval)
                    _hooks[ON_RETRY](args, kwargs, wrapper_obj.outcome, wrapper_obj.exception)
                    cur_retry_times += 1
                    continue

                if wrapper_obj.exception:
                    raise wrapper_obj.exception
                _hooks[ON_SUCCESS](args, kwargs, wrapper_obj.outcome, wrapper_obj.exception)
                return wrapper_obj.outcome

        return wrapper

    return inner


def when_exceptions_type(*exceptions):
    def retry_when(args, kwargs, outcome, exception):
        return isinstance(exception, exceptions)

    return retry_when


def unless_exceptions_type(*exceptions):
    def retry_when(args, kwargs, outcome, exception):
        return exception is not None and not isinstance(exception, exceptions)

    return retry_when


def when_is_result(result):
    def retry_when(args, kwargs, outcome, exception):
        return result is outcome if isinstance(outcome, bool) else result == outcome

    return retry_when


def when_is_not_result(result):
    def retry_when(args, kwargs, outcome, exception):
        return result is not outcome if isinstance(outcome, bool) else result != outcome

    return retry_when
