from typing import TYPE_CHECKING

from hyx.common.events import ListenerRegistry

if TYPE_CHECKING:
    from hyx.timeout.manager import TimeoutManager


_TIMEOUT_LISTENERS: ListenerRegistry["TimeoutListener"] = ListenerRegistry()


class TimeoutListener:
    """
    Listen to events dispatched by timeout components
    """

    async def on_timeout(self, timeout: "TimeoutManager") -> None:
        """
        Dispatch on timing out
        """


def register_timeout_listener(listener: TimeoutListener) -> None:
    """
    Register a listener that will listen to all timeout components in the system
    """
    global _TIMEOUT_LISTENERS

    _TIMEOUT_LISTENERS.register(listener)
