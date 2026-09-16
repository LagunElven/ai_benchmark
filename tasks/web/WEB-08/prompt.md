# Guarded Ionic-style navigation

Implement `createNavigator(initialRoute, canLeave)`. It returns `current()`,
`history()`, and asynchronous `navigate(route)`, `replace(route)` and `back()` methods.
The initial route must be a nonblank string, and every target route must also be a
nonblank string.

`navigate` pushes a route, `replace` swaps the current route without growing the stack,
and `back` pops one route. Before every real transition, await `canLeave(from, to)`;
only a truthy result commits the transition. A false result leaves the stack unchanged.
If the guard rejects, propagate that error and leave the stack unchanged. Going back
from the root route is a no-op and must not invoke the guard. `history()` must return a
copy, and navigating to the current route is a no-op. Do not add Ionic dependencies or
modify the tests.
