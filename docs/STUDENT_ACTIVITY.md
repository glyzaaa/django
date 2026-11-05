# Student activity: website remix with queues and singly linked lists

## Your objective

Start the server, create your Django account/workspace, and keep authentication
and role checks intact while remixing. Teammates use their own accounts; the
workspace owner creates invitation links under Team members. A viewer can read
but cannot run modifying operations. Each team can keep its work separate.


Choose a useful purpose for the website and make meaningful frontend changes.
At the same time, complete **both** backend data-structure activities. Keep the
real Service queue and Workflow pages connected to your classes.

Possible concepts include a campus helpdesk, a library request desk, an event
support board, a document review desk or a game lobby request manager. Explain
which users your changes help. Name/accent settings alone are not a full remix.

The supplied website already works. The unfinished behavior is intentional:
requests leave newest first, and workflow methods use flat storage.

## Activity A: FIFO queue

Edit **`backend/dsa/queue.py`**. Preserve `ServiceQueue` and this interface:

| Member | Contract |
| --- | --- |
| `ServiceQueue(items=None)` | Load saved values in earliest-to-latest arrival order; do not mutate the input |
| `enqueue(value)` | Add at the rear; no return value is required |
| `dequeue()` | Remove and return the earliest item still waiting |
| `peek()` | Read that same front value without removal |
| `is_empty()` | Return True only when no values remain |
| `size()` | Return the count |
| `to_list()` | Return a NEW list in arrival order, front to rear |

Empty `dequeue()` and `peek()` must raise `IndexError`. The website catches the
empty situation and shows a useful message. Duplicates are valid at the class
level; the application separately prevents the same ticket ID joining twice.

Use a representation that supports O(1) enqueue and dequeue. A solution using
`pop(0)` on an ordinary Python list changes FIFO behavior but shifts remaining
references, so it does not meet that efficiency goal. Your instructor reviews
the representation and complexity; passing behavioral tests alone cannot prove
an asymptotic complexity claim.

### Follow the actual feature

1. Join queue calls `services.enqueue_ticket()`.
2. That service reconstructs `ServiceQueue(workspace.queue_state)` and calls `enqueue()`.
3. Django saves `to_list()` through the Workspace model.
4. The queue page reconstructs the class and calls `peek()`.
5. Start next request (serve) calls `dequeue()` and moves the returned ticket to In progress.

Do not replace the real class call with an ORM ordering trick or rearranged
HTML. `challenge/test_queue.py` tests the real serve route and saved records.

### Required queue demonstration

- Create A, B and C as To do items. Join A, B and C in that order.
- Before editing, record the baseline's selected next item.
- After editing, repeatedly peek and show that count/order remain unchanged.
- Serve A. Join D. The remaining service order must be B, C, D.
- Refresh between each action and confirm saved state stays correct.
- Serve the last item, then submit an empty serve request safely.
- Run `CHECK_QUEUE.bat` and keep the output.

The priority badge is descriptive; this activity's service order is FIFO.
Changing an item out of To do or archiving it cancels its waiting position.
Restoring an archived item does not automatically rejoin the queue.

## Activity B: real singly linked nodes

Edit **`backend/dsa/singly_linked_list.py`**. A `Node` class is already supplied.
Replace the flat backing collection in `SinglyLinkedList` with Node objects.

- `head` refers to the first data node, or None when empty.
- `tail` refers to the final data node, or None when empty.
- Every node has `data` and `next`; the final next is None.
- `_size` stores the node count. Keep it synchronized after mutations.
- The constructor accepts an optional iterable and builds the actual chain.
- Surviving nodes must retain their identities when you insert/remove another
  node. Rebuilding every node from a hidden Python list is not the target.
- Do not keep a persistent list, tuple, dictionary, set or deque as the backing
  collection. A temporary output list in `to_list()` is allowed.

Keep the existing method names and return rules:

| Method | Contract |
| --- | --- |
| `prepend(value)` | Insert a new head |
| `append(value)` | Insert after tail |
| `insert_at(index, value)` | Insert at 0 through size, inclusive |
| `remove_at(index)` | Remove at 0 through size minus 1 and return its data |
| `remove(value)` | Remove the first matching value and return True; return False when missing |
| `get(index)` | Read data at that index without mutation |
| `index_of(value)` | Return the first matching index, or -1 |
| `size()` | Return the cached count |
| `is_empty()` | Return whether the count is zero |
| `to_list()` | Traverse head to tail and return a NEW list of values |

Indices must be integers. The provided `require_integer()` helper rejects
strings, fractional values and booleans. Negative or out-of-range integers
raise `IndexError`. Keep these checks while replacing the storage.

### Follow the actual feature

An operation form on Workflow reaches `operate_workflow()` in
`backend/workspace/services.py`. The service reconstructs your class from the
saved values, calls the chosen method and saves a new snapshot. Search/get also
record their returned result without changing the workflow values.

The structure inspector reads actual `head`, `tail` and `next` references.
It deliberately does not draw node links for the starter's flat collection.
The inspector is a teaching aid; the complete goal checker also inspects
representation and mutation behavior.

### Required linked-list demonstration

1. Remove the initial example steps so the workflow is empty.
2. Append text values `10`, `20`, `30`.
3. `prepend(5)` produces `[5, 10, 20, 30]`.
4. `insert_at(2, 15)` produces `[5, 10, 15, 20, 30]`.
5. `remove_at(3)` returns `20` and leaves `[5, 10, 15, 30]`.
6. `append(40)` leaves `[5, 10, 15, 30, 40]`.
7. `index_of(30)` returns `3`; `get(2)` returns `15`.
8. Show head, tail and the final next reference in the inspector.
9. Show a missing value, duplicates, an invalid index and deletion of the only node.
10. Refresh between operations and run `CHECK_LINKED_LIST.bat`.

The web form treats values as **text labels**. Class-level tests also use
numbers, so do not force all Node data to strings inside the data structure.

## Complexity to explain

For a correct implementation with head, tail and a cached count:

| Operation | Target time |
| --- | --- |
| Queue enqueue/dequeue/peek/size/empty | O(1) |
| Linked-list prepend/append/remove_at(0)/size/empty | O(1) |
| General get/search/middle insertion/middle removal | O(n) worst case |
| Removing the final node in a singly linked list | O(n) to find its predecessor |
| `to_list()` and loading a saved snapshot | O(n) |

These are data-structure costs. A whole HTTP request also reloads/saves values,
performs database work and renders a page. Do not describe the entire web
request as O(1) just because its queue end operation is O(1).

## Website remix

Use `frontend/templates/` for Django HTML, `frontend/static/app.css` for design,
and `frontend/static/app.js` for browser behavior. You may add useful fields,
pages or features; update Django models/forms/migrations when appropriate.
Keep required methods and real application integration intact.

Verify your remix on a narrow phone-sized screen, check form labels/errors,
and explain why the changes help your chosen audience. All local assets are
included; do not replace the working favicon with a file that is absent from
your repository.

## Verification and submission

Run `RUN_TESTS.bat`, `CHECK_ACTIVITY.bat` and then `RUN_ALL_CHECKS.bat`. Application
checks should pass both before and after the solution. The combined activity
goal should pass after both classes are implemented.

Submit source code, a setup README, screenshots/recording showing both required
demonstrations, checker output, the before/after explanation and a contribution
table. Each member must explain a real contribution. Exclude generated data,
local keys, caches and virtual environments. Do not modify the goal tests.

| Suggested criterion | Points |
| --- | ---: |
| Correct FIFO queue and efficient representation | 25 |
| Real singly linked nodes and correct methods/edge cases | 35 |
| Useful website concept and meaningful frontend remix | 20 |
| Working Django/SQLite integration after changes | 10 |
| Individual explanation and contribution evidence | 10 |
| Total | 100 |

Optional extension after both goals pass: make `ServiceQueue` use your actual
singly linked list, appending at tail and removing at head. This connects to
lecture slides 38-39 without changing the website's public interface.
