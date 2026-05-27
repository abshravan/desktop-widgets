# widget_registry.py — Central catalogue of every widget the launcher offers.
#
# To add a new widget, write it under widgets/, then add one entry here.
# Each entry specifies how the launcher should display & instantiate it.

from widgets.clock_widget          import ClockWidget
from widgets.battery_widget        import BatteryWidget
from widgets.weather_widget        import WeatherWidget
from widgets.news_widget           import NewsWidget
from widgets.system_monitor_widget import SystemMonitorWidget
from widgets.pomodoro_widget       import PomodoroWidget
from widgets.todo_widget           import TodoWidget
from widgets.notes_widget          import NotesWidget
from widgets.calculator_widget     import CalculatorWidget
from widgets.calendar_widget       import CalendarWidget
from widgets.network_widget        import NetworkWidget
from widgets.timer_widget          import TimerWidget
from widgets.world_clock_widget    import WorldClockWidget
from widgets.crypto_widget         import CryptoWidget
from widgets.clipboard_widget      import ClipboardWidget
from widgets.disk_widget           import DiskWidget
from widgets.now_playing_widget    import NowPlayingWidget
import config


WIDGET_REGISTRY = {
    "clock": {
        "label":    "Clock",
        "icon":     "🕐",
        "factory":  lambda: ClockWidget(),
        "width":    240,
        "default":  (60, 60),
    },
    "world_clock": {
        "label":    "World Clock",
        "icon":     "🌍",
        "factory":  lambda: WorldClockWidget(),
        "width":    250,
        "default":  (60, 320),
    },
    "system": {
        "label":    "System Monitor",
        "icon":     "📊",
        "factory":  lambda: SystemMonitorWidget(),
        "width":    280,
        "default":  (340, 60),
    },
    "network": {
        "label":    "Network",
        "icon":     "📡",
        "factory":  lambda: NetworkWidget(),
        "width":    280,
        "default":  (340, 220),
    },
    "disk": {
        "label":    "Disk Usage",
        "icon":     "💾",
        "factory":  lambda: DiskWidget(),
        "width":    280,
        "default":  (340, 380),
    },
    "battery": {
        "label":    "Battery",
        "icon":     "🔋",
        "factory":  lambda: BatteryWidget(config.BATTERY_REFRESH_INTERVAL),
        "width":    250,
        "default":  (340, 580),
    },
    "pomodoro": {
        "label":    "Pomodoro",
        "icon":     "🍅",
        "factory":  lambda: PomodoroWidget(),
        "width":    230,
        "default":  (640, 60),
    },
    "timer": {
        "label":    "Timer",
        "icon":     "⏱",
        "factory":  lambda: TimerWidget(),
        "width":    240,
        "default":  (640, 280),
    },
    "todo": {
        "label":    "Todo List",
        "icon":     "✓",
        "factory":  lambda: TodoWidget(),
        "width":    290,
        "default":  (640, 480),
    },
    "notes": {
        "label":    "Notes",
        "icon":     "📝",
        "factory":  lambda: NotesWidget(),
        "width":    290,
        "default":  (950, 60),
    },
    "calculator": {
        "label":    "Calculator",
        "icon":     "🧮",
        "factory":  lambda: CalculatorWidget(),
        "width":    240,
        "default":  (950, 340),
    },
    "calendar": {
        "label":    "Calendar",
        "icon":     "📅",
        "factory":  lambda: CalendarWidget(),
        "width":    280,
        "default":  (950, 600),
    },
    "clipboard": {
        "label":    "Clipboard",
        "icon":     "📋",
        "factory":  lambda: ClipboardWidget(),
        "width":    290,
        "default":  (1260, 60),
    },
    "now_playing": {
        "label":    "Now Playing",
        "icon":     "🎵",
        "factory":  lambda: NowPlayingWidget(),
        "width":    270,
        "default":  (1260, 320),
    },
    "weather": {
        "label":    "Weather",
        "icon":     "☀",
        "factory":  lambda: WeatherWidget(config.WEATHER_REFRESH_INTERVAL),
        "width":    250,
        "default":  (1260, 520),
    },
    "crypto": {
        "label":    "Crypto",
        "icon":     "₿",
        "factory":  lambda: CryptoWidget(),
        "width":    260,
        "default":  (1260, 720),
    },
    "news": {
        "label":    "News",
        "icon":     "📰",
        "factory":  lambda: NewsWidget(config.NEWS_REFRESH_INTERVAL),
        "width":    320,
        "default":  (1560, 60),
    },
}
