import logging
from typing import Callable

from PyQt6 import QtWidgets


logger = logging.getLogger(__name__)


def get_navigation_manager():
    app = QtWidgets.QApplication.instance()
    return getattr(app, "navigation_manager", None) if app is not None else None


class NavigationManager:
    """Shared app-level router with stack-based back navigation and route reuse."""

    def __init__(self) -> None:
        self._routes: dict[str, Callable[[], QtWidgets.QWidget]] = {}
        self._instances: dict[str, QtWidgets.QWidget] = {}
        self._history: list[str] = []
        self.current_route: str | None = None

    def register_route(self, route_name: str, factory: Callable[[], QtWidgets.QWidget]) -> None:
        self._routes[route_name] = factory

    def set_route_instance(self, route_name: str, widget: QtWidgets.QWidget) -> None:
        self._instances[route_name] = widget

    def navigate(self, current_window: QtWidgets.QWidget | None, target_route: str) -> QtWidgets.QWidget:
        if target_route not in self._routes and target_route not in self._instances:
            raise ValueError(f"Unknown route: {target_route}")

        source_route = self._route_for_widget(current_window) or self.current_route

        if source_route and source_route != target_route:
            self._history.append(source_route)

        next_window = self._get_or_create(target_route)

        logger.info("Route change: %s -> %s", source_route or "(none)", target_route)
        self.current_route = target_route

        self._transition(current_window, next_window)
        return next_window

    def back(self, current_window: QtWidgets.QWidget | None, fallback_route: str = "main") -> QtWidgets.QWidget:
        while self._history:
            target_route = self._history.pop()
            if target_route in self._routes or target_route in self._instances:
                break
        else:
            target_route = fallback_route

        source_route = self._route_for_widget(current_window) or self.current_route
        next_window = self._get_or_create(target_route)

        logger.info("Route change: %s -> %s", source_route or "(none)", target_route)
        self.current_route = target_route
        self._transition(current_window, next_window)
        return next_window

    def _get_or_create(self, route_name: str) -> QtWidgets.QWidget:
        if route_name not in self._instances:
            self._instances[route_name] = self._routes[route_name]()
        return self._instances[route_name]

    def _route_for_widget(self, widget: QtWidgets.QWidget | None) -> str | None:
        if widget is None:
            return None
        for route_name, route_widget in self._instances.items():
            if route_widget is widget:
                return route_name
        return None

    @staticmethod
    def _transition(current_window: QtWidgets.QWidget | None, next_window: QtWidgets.QWidget) -> None:
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.current_window = next_window

        if current_window is not None and current_window is not next_window:
            current_window.hide()

        next_window.show()
