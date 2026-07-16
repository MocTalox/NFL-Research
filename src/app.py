import webview

from bridge import ApiBridge


window = webview.create_window( # pyright: ignore[reportUnknownMemberType]
    "Pokemon TGR Breakpoint Damage Calculator",
    "../ui/index.html",
    js_api=ApiBridge()
)

webview.start()
