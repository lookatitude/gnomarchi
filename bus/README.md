# gnomarchi-bus (stub)

Session D-Bus service for summoning the menu, theme-apply events, plugin enable signals, and Agents window open.

| Constant | Value |
| --- | --- |
| Bus name | `org.gnomarchi.Bus` (provisional) |
| Object path | `/org/gnomarchi/Bus` |
| Interface | `org.gnomarchi.Bus1` |

Transport: session bus; JSON payloads for non-primitive args. UI never shells out with user secrets; CLI is the privileged edge for pack writes under `$XDG_CONFIG_HOME/gnomarchi`.

Python stubs: `client.py` / `server.py` use an in-process Unix socket fallback when D-Bus is unavailable (dev/tests).
