# Instructor guide

## Distribution

Distribute **the student application ZIP** only. It contains the complete
website and intentionally unfinished student classes. The separate instructor
download contains complete reference implementations; do not add it to the
student repository.

The original inspect/change/verify activity is preserved. Service queue now
supplies the ordering problem. Workflow supplies the representation problem.
Archive is ordinary individual-item restore, with no assessed ordering rule.

## Two-lecture sequence

| Lecture | Demonstration | Student task |
| --- | --- | --- |
| 1: Queues | Create A/B/C, join in order, observe newest selected | Modify `backend/dsa/queue.py` to implement FIFO |
| 2: Singly linked lists | Run workflow methods and observe flat storage | Replace `backend/dsa/singly_linked_list.py` with actual nodes |

Keep the visible lecture material as the conceptual guide. Use
`docs/REFERENCES.md` for the exact slide mapping and method names.

## First demonstration

1. Extract into a new folder, run SETUP.bat, then START.bat, and create your own account.
2. Show the board/list views, create/edit form, queue and workflow.
3. Explain the folder map: frontend, backend, database.
4. Create A/B/C as To do items. Join A, B, C.
5. The baseline selects C. FIFO must select A.
6. Run RUN_TESTS.bat: 57 application tests should pass.
7. Run CHECK_QUEUE.bat: 7 of 10 tests fail on the untouched starter.
8. Open Workflow: methods work, but the inspector labels flat storage.
9. Run CHECK_LINKED_LIST.bat: 7 of 17 tests fail on the untouched starter.

These exact failure counts describe this shipped baseline. A student's partial
implementation may fail different checks. Syntax/import errors are different
from the expected assertion failures and must be fixed.

## Why two challenges

Activity A tests service behavior. The backend result determines the actual
ticket moved to In progress and the event log's item ID. Activity B tests
storage representation as well as functional output. A Python list can mimic
the visible results, so the goal checker follows actual nodes and checks that
surviving Node objects are not rebuilt on each mutation.

Both features persist snapshots in the same SQLite database. Reconstructing
nodes from a snapshot on the next request is expected. Within an individual
data-structure operation, preserve surviving nodes and rewire links.

## What the project supplies

The instructor does not need to implement Django forms, CSRF, sessions,
templates, database models/migrations, item CRUD, search, archive/restore,
preferences, the activity log or basic mobile layouts. Student DSA work is
localized to two files. Students also remix frontend/content for their concept.

Accounts are real Django identities. Each registration creates an owned
workspace. To collaborate, create email-bound invitations under Team members.
Agents can edit requests and run both activities; viewers can only read.
Membership, not browser identity, determines access across devices. No default
administrator or password is shipped. Keep your instructor workspace separate
from students' independent workspaces if demonstrating completed algorithms.

## Review more than a green test run

- Why does FIFO select A? What happens if a new arrival joins after one removal?
- Which service calls the class, and which database row changes?
- Why must `to_list()` keep its storage contract?
- What are the empty and single-node invariants?
- Where does middle insertion spend its O(n) time?
- Why is a temporary result list allowed while flat backing storage is not?
- What can and cannot be concluded from the inspector's node label?
- What happens after refresh or server restart?
- Why can serialization make the HTTP request O(n) even with O(1) queue operations?
- How do the website changes help the proposed users?

The tests verify behavior and selected structural invariants. Read the code
and ask students to justify complexity. A behavioral test suite cannot prove
all asymptotic performance properties or replace individual assessment.

Use the 100-point suggested rubric in STUDENT_ACTIVITY.md, or adjust it before
assigning the activity. Deadline and team size are intentionally not invented.

## Instructor reference verification

In a separate copy of the student project, install the two completed files
from the instructor download. Run RUN_ALL_CHECKS.bat. All 84 checks should pass.
The optional instructor queue_using_nodes.py also passes with the real linked
list and illustrates lecture slides 38-39. Keep your original student copy
unfinished so future distributions retain the assignment.
