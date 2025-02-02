import functools
from typing import Any, Callable, Optional, Sequence, cast
from hyx.common.events import EventDispatcher
from hyx.common.typing import ExceptionsT, FuncT
from hyx.ratelimit.managers import TokenBucketLimiter
from hyx.retry.listeners import RetryListener
from hyx.retry.manager import RetryManager
from hyx.retry.typing import AttemptsT, BackoffsT, BucketRetryT

def retry(
    *,
    on: ExceptionsT = Exception,
    attempts: AttemptsT = 3,
    backoff: BackoffsT = 0.5,
    name: Optional[str] = None,
    listeners: Optional[Sequence[RetryListener]] = None,
) -> Callable[[Callable], Callable]:
    """
    `@retry()` decorator retries the function `on` exceptions for the given number of `attempts`.
        Delays after each retry is defined by `backoff` strategy.

    **Parameters:**

    * **on** - Exception or tuple of Exceptions we need to retry on.
    * **attempts** - How many times do we need to retry. If `None`, it will infinitely retry until the success.
    * **backoff** - Backoff Strategy that defines delays on each retry.
        Takes `float` numbers (delay in secs), `list[floats]` (delays on each retry attempt), or `Iterator[float]`
    * **name** *(None | str)* - A component name or ID (will be passed to listeners and mention in metrics)
    * **listeners** *(None | Sequence[TimeoutListener])* - List of listeners of this concreate component state
    """
    manager = RetryManager(
        name=name,
        exceptions=on,
        attempts=attempts,
        backoff=backoff,
        event_dispatcher=EventDispatcher(listeners).as_listener,
    )

    def _decorator(func: FuncT) -> FuncT:
        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(cast(FuncT, functools.partial(func, *args, **kwargs)))

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = manager  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)

    return _decorator

def bucket_retry(
    *,
    on: ExceptionsT = Exception,
    attempts: AttemptsT = 3,
    backoff: BackoffsT = 0.5,
    name: Optional[str] = None,
    listeners: Optional[Sequence[RetryListener]] = None,
    per_time_secs: BucketRetryT = 1,
    bucket_size: BucketRetryT = 3
) -> Callable[[Callable], Callable]:
    """
    `@bucket_retry()` decorator retries until we have tokens in the bucket and at most that number of times per request.

    """
    limiter = (
        TokenBucketLimiter(attempts, per_time_secs, bucket_size)
        if attempts and per_time_secs
        else None
    )
    
    manager = RetryManager(
        name=name,
        exceptions=on,
        attempts=attempts,
        backoff=backoff,
        event_dispatcher=EventDispatcher(listeners).as_listener,
        limiter=limiter,
    )

    def _decorator(func: FuncT) -> FuncT:
        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(cast(FuncT, functools.partial(func, *args, **kwargs)))

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = manager  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)

    return _decorator
