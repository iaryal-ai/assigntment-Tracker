from dataclasses import dataclass
from drafter import *

set_website_title("Assigntment Tracker")
set_site_information(
    author="Ishaan Aryal",
    description="Tracking assigmentment",
    sources="Thanks to the Drafter docs and my study group.",
    planning=["CS1 Final Project 0_ Pick a Problem.pdf", "CS1 Final Project 1_ Design (1).pdf", "cisc final llm conversation.pdf"],
    links=["https://drive.google.com/drive/folders/1d2lI9GvajqjMHn_KXzXI7G9igT_P6-Vr?usp=drive_link"]
)
hide_debug_information()
set_website_framed(False)



# @dataclass automatically creates useful methods such as __init__.
@dataclass
class Assignment:
    """Store the information for one assignment."""

    course: str
    name: str
    due_date: str
    # The union type allows a percentage grade or None before grading.
    grade: float | None
    completed: bool


# State is passed between Drafter routes to keep the website's data.
@dataclass
class State:
    """Store all information that the assignment tracker needs."""

    assignments: list[Assignment]
    classes: list[str]
    completed: list[Assignment]
    completed_amount: int


def grade_letter(grade: float) -> str:
    """Convert a percentage grade into a letter grade."""
    if grade > 90:
        return "A"
    elif grade > 80:
        return "B"
    elif grade > 70:
        return "C"
    elif grade > 60:
        return "D"
    else:
        return "F"



def course_average(assignments: list[Assignment], course_name: str) -> float | None:
    """Return the average of graded assignments for one course.

    Assignments without grades are excluded. Return None if no grades exist.
    """
    grades = []

    for assignment in assignments:
        if assignment.course == course_name and assignment.grade is not None:
            grades.append(assignment.grade)

    if len(grades) == 0:
        return None

    return sum(grades) / len(grades)


def assignment_description(assignment: Assignment) -> str:
    """Create a readable line containing an assignment's information."""
    description = (
        assignment.course + " | " + assignment.name
        + " | Due: " + assignment.due_date
    )

    if assignment.grade is None:
        description = description + " | Grade: Not entered"
    else:
        letter = grade_letter(assignment.grade)
        description = (
            description + " | Grade: " + str(assignment.grade)
            + "% (" + letter + ")"
        )

    return description


def navigation_buttons() -> list:
    """Return spaced navigation buttons for the bottom of each page."""
    return [
        Header("Navigation", level=2),
        Button("Home", "index"),
        Button("Classes", "classes"),
        Button("Assignments", "assignments"),
        Button("Add Assignment", "addAssignment"),
        Button("Grades", "grades"),
        Button("Completed", "completed"),
        Button("Delete Assignment", "deleteAssignment"),
        Button("About", "about"),
    ]


# @route connects each function to a page that Drafter can display.
@route
def index(state: State) -> Page:
    """Show a spacious home page with descriptions of every website section."""
    content = [
        Header("Student Assignment Tracker"),
        "Welcome! Use this website to organize your courses and keep track "
        "of your schoolwork.",
        Header("Your Progress", level=2),
        "Assignments completed: " + str(state.completed_amount),
        "Classes added: " + str(len(state.classes)),
        "Assignments created: " + str(len(state.assignments)),
        Header("Manage Your Courses", level=2),
        "View/edit your classes:",
        Button("Go to Classes", "classes"),
        Header("Manage Your Assignments", level=2),
        "Assignments:",
        Button("View Assignments", "assignments"),
        "Add Assignment:",
        Button("Add an Assignment", "addAssignment"),
        Header("Review Your Work", level=2),
        "Grades:",
        Button("View Grades", "grades"),
        "Completed assigments:",
        Button("View Completed Work", "completed"),
        Header("Other Tools", level=2),
        "Delete Assignment: ",
        Button("Delete an Assignment", "deleteAssignment"),
        "About: ",
        Button("About This Website", "about"),
    ]
    return Page(state, content)


@route
def classes(state: State) -> Page:
    """Show the class form first, followed by one class name per line."""
    content = [
        Header("Your Classes"),
        "Add a class using the textbox below.",
        "New class name:",
        TextBox("course_name"),
        Button("Add Class", "addClass"),
        LineBreak(),
        LineBreak(),
        "Classes:",
        LineBreak(),
    ]

    if len(state.classes) == 0:
        content.append("You have not added any classes yet.")
    else:
        for course_name in state.classes:
            content.append(course_name + ",")
            content.append(LineBreak())

    content.extend(navigation_buttons())
    return Page(state, content)


@route
def addClass(state: State, course_name: str) -> Page:
    """Add a new class if its name is not blank or already in the list."""
    cleaned_name = course_name.strip()

    if cleaned_name == "":
        return Page(state, [
            Header("Class Not Added"),
            "Please enter a class name.",
            Button("Back to Classes", "classes"),
        ])

    if cleaned_name not in state.classes:
        state.classes.append(cleaned_name)

    return classes(state)


@route
def assignments(state: State) -> Page:
    """Show assignments grouped by course, with each assignment on a new line."""
    content = [
        Header("Assignments"),
        "Assignments are grouped by the course they belong to.",
        "When you finish an assignment, mark it complete and enter its grade "
        "below.",
        LineBreak(),
    ]

    if len(state.assignments) == 0:
        content.append("You have no assignments yet.")
    else:
        for course_name in state.classes:
            course_has_assignments = False

            for assignment in state.assignments:
                if assignment.course == course_name:
                    course_has_assignments = True

            if course_has_assignments:
                content.append(Header(course_name, level=2))

                for position in range(len(state.assignments)):
                    assignment = state.assignments[position]

                    if assignment.course == course_name:
                        content.append(assignment_description(assignment))
                        content.append(LineBreak())

                        if assignment.completed == False:
                            content.append(
                                Button(
                                    "Mark Complete",
                                    "completeAssignment",
                                    {"position": position},
                                )
                            )
                        elif assignment.grade is None:
                            content.append("Enter the grade you received:")
                            content.append(LineBreak())
                            content.append(TextBox("grade", 0.0, "number"))
                            content.append(
                                Button(
                                    "Save Grade",
                                    "saveGrade",
                                    {"position": position},
                                )
                            )
                        else:
                            content.append("Grade saved.")

                        content.append(LineBreak())
                        content.append(LineBreak())

    content.extend(navigation_buttons())
    return Page(state, content)


@route
def addAssignment(state: State) -> Page:
    """Show the form used to create an assignment without entering a grade."""
    content = [
        Header("Add an Assignment"),
        "Enter the assignment name, choose its course, and add its due date.",
        "You will enter the grade later, after marking the assignment complete.",
    ]

    if len(state.classes) == 0:
        content.append("You need to add a class before creating an assignment.")
        content.append(Button("Go to Classes", "classes"))
    else:
        content.extend([
            "Assignment name:",
            TextBox("assignment_name"),
            "Course:",
            # SelectBox lets the user choose from the classes already created.
            SelectBox("course", state.classes),
            "Due date (example: 11/20/2026):",
            TextBox("due_date"),
            Button("Create Assignment", "saveAssignment"),
        ])

    content.extend(navigation_buttons())
    return Page(state, content)


@route
def saveAssignment(
    state: State,
    assignment_name: str,
    course: str,
    due_date: str,
) -> Page:
    """Validate the form and add an ungraded assignment to the main list."""
    cleaned_name = assignment_name.strip()
    cleaned_date = due_date.strip()

    if cleaned_name == "":
        return Page(state, [
            Header("Assignment Not Added"),
            "Please enter an assignment name.",
            Button("Try Again", "addAssignment"),
        ])

    if cleaned_date == "":
        return Page(state, [
            Header("Assignment Not Added"),
            "Please enter a due date.",
            Button("Try Again", "addAssignment"),
        ])

    if course not in state.classes:
        return Page(state, [
            Header("Invalid Course"),
            "Please choose a class from your class list.",
            Button("Try Again", "addAssignment"),
        ])

    new_assignment = Assignment(
        course,
        cleaned_name,
        cleaned_date,
        None,
        False,
    )
    state.assignments.append(new_assignment)
    return assignments(state)


# Button route arguments (such as position) identify which assignment to update.
@route
def completeAssignment(state: State, position: int) -> Page:
    """Mark one assignment complete and update the completed list and count."""
    if position >= 0 and position < len(state.assignments):
        assignment = state.assignments[position]

        if assignment.completed == False:
            assignment.completed = True
            state.completed.append(assignment)
            state.completed_amount = state.completed_amount + 1

    return assignments(state)


@route
def saveGrade(state: State, position: int, grade: float) -> Page:
    """Save a percentage grade for an assignment that has been completed."""
    if position < 0 or position >= len(state.assignments):
        return assignments(state)

    assignment = state.assignments[position]

    if assignment.completed == False:
        return assignments(state)

    if grade < 0 or grade > 100:
        return Page(state, [
            Header("Invalid Grade"),
            "Please enter a grade between 0 and 100.",
            Button("Return to Assignments", "assignments"),
        ])

    assignment.grade = grade
    return assignments(state)


@route
def grades(state: State) -> Page:
    """Show assignment grades and the average grade for each course."""
    content = [
        Header("Assignment Grades"),
        "Grades are entered from the Assignments page after work is completed.",
        LineBreak(),
    ]

    found_grade = False

    for course_name in state.classes:
        average = course_average(state.assignments, course_name)

        if average is not None:
            found_grade = True
            content.append(Header(course_name, level=2))
            content.append(
                "Course average: " + str(round(average, 2)) + "%"
            )
            content.append(LineBreak())

            for assignment in state.assignments:
                if assignment.course == course_name:
                    if assignment.grade is not None:
                        content.append(assignment_description(assignment))
                        content.append(LineBreak())

            content.append(LineBreak())

    if found_grade == False:
        content.append("No grades have been entered yet.")

    content.extend(navigation_buttons())
    return Page(state, content)


@route
def completed(state: State) -> Page:
    """Show completed assignments, with each assignment on its own line."""
    content = [
        Header("Completed Assignments"),
        "Total completed: " + str(state.completed_amount),
        "You can enter a grade for completed work from the Assignments page.",
        LineBreak(),
    ]

    if len(state.completed) == 0:
        content.append("You have not completed any assignments yet.")
    else:
        for assignment in state.completed:
            content.append(assignment_description(assignment))
            content.append(LineBreak())

    content.extend(navigation_buttons())
    return Page(state, content)


@route
def deleteAssignment(state: State) -> Page:
    """List assignments and ask for confirmation before deleting one."""
    content = [
        Header("Delete an Assignment"),
        "Choose an assignment below. You will be asked to confirm before "
        "it is permanently deleted.",
        LineBreak(),
    ]

    if len(state.assignments) == 0:
        content.append("There are no assignments to delete.")
    else:
        for position in range(len(state.assignments)):
            assignment = state.assignments[position]
            content.append(assignment_description(assignment))
            content.append(LineBreak())
            content.append(
                Button(
                    "Delete This Assignment",
                    "confirmDelete",
                    {"position": position},
                )
            )
            content.append(LineBreak())
            content.append(LineBreak())

    content.extend(navigation_buttons())
    return Page(state, content)


@route
def confirmDelete(state: State, position: int) -> Page:
    """Ask the user to confirm the selected assignment deletion."""
    if position < 0 or position >= len(state.assignments):
        return deleteAssignment(state)

    assignment = state.assignments[position]
    return Page(state, [
        Header("Confirm Deletion"),
        "Are you sure you want to permanently delete this assignment?",
        LineBreak(),
        assignment_description(assignment),
        LineBreak(),
        Button(
            "Yes, Delete Assignment",
            "removeAssignment",
            {"position": position},
        ),
        Button("No, Go Back", "deleteAssignment"),
    ])


@route
def removeAssignment(state: State, position: int) -> Page:
    """Delete an assignment after confirmation and update completed tracking."""
    if position >= 0 and position < len(state.assignments):
        assignment = state.assignments.pop(position)

        if assignment.completed == True:
            if assignment in state.completed:
                state.completed.remove(assignment)
            state.completed_amount = state.completed_amount - 1

    return deleteAssignment(state)


@route
def about(state: State) -> Page:
    """Explain how to use the assignment tracker in a numbered list."""
    return Page(state, [
        Header("About This Website"),
        # NumberedList displays each instruction with an aligned number.
        NumberedList([
            "Open Classes and add the courses you are taking.",
            "Open Add Assignment to enter an assignment name, course, "
            "and due date.",
            "Open Assignments to see your work organized by course.",
            "When you finish an assignment, click Mark Complete.",
            "Enter the percentage grade in the Assignments page and "
            "click Save Grade.",
            "Open Grades to review the grades you have entered.",
            "Open Completed to review finished assignments.",
            "Open Delete Assignment to remove an assignment.",
        ]),
        "link to repository: https://github.com/iaryal-ai/assigntment-Tracker.",
        Button("Back Home", "index"),
    ])


def run_tests() -> None:
    """Run unit tests for grade calculations and assignment-management routes.

    The tests use separate State objects so they do not change the live website.
    """
    # Test letter-grade boundaries and representative percentages.
    assert_equal(grade_letter(95), "A")
    assert_equal(grade_letter(91), "A")
    assert_equal(grade_letter(90), "B")
    assert_equal(grade_letter(85), "B")
    assert_equal(grade_letter(80), "C")
    assert_equal(grade_letter(75), "C")
    assert_equal(grade_letter(70), "D")
    assert_equal(grade_letter(65), "D")
    assert_equal(grade_letter(60), "F")
    assert_equal(grade_letter(50), "F")

    # Test the course-average helper, including assignments without grades.
    average_assignments = [
        Assignment("CISC 108", "Quiz 1", "11/20", 80.0, True),
        Assignment("CISC 108", "Quiz 2", "11/21", 100.0, True),
        Assignment("CISC 108", "Homework", "11/22", None, False),
        Assignment("PHYS 207", "Quiz 1", "11/23", 70.0, True),
    ]
    assert_equal(course_average(average_assignments, "CISC 108"), 90.0)
    assert_equal(course_average(average_assignments, "PHYS 207"), 70.0)
    assert_equal(course_average(average_assignments, "MATH 241"), None)

    # Test adding a class and rejecting blank or duplicate class names.
    class_state = State([], [], [], 0)
    addClass(class_state, "PHYS 207")
    assert_equal(class_state.classes, ["PHYS 207"])
    addClass(class_state, "PHYS 207")
    assert_equal(class_state.classes, ["PHYS 207"])
    addClass(class_state, "   ")
    assert_equal(class_state.classes, ["PHYS 207"])

    # Test creating an assignment with no grade entered yet.
    assignment_state = State([], ["CISC 108"], [], 0)
    saveAssignment(
        assignment_state,
        "Project",
        "CISC 108",
        "11/20/2026",
    )
    assert_equal(len(assignment_state.assignments), 1)
    assert_equal(assignment_state.assignments[0].name, "Project")
    assert_equal(assignment_state.assignments[0].grade, None)
    assert_equal(assignment_state.assignments[0].completed, False)

    # Test that invalid assignment information does not add an assignment.
    saveAssignment(assignment_state, " ", "CISC 108", "11/20/2026")
    saveAssignment(assignment_state, "Missing date", "CISC 108", " ")
    saveAssignment(assignment_state, "Wrong course", "MATH 101", "11/20/2026")
    assert_equal(len(assignment_state.assignments), 1)

    # Test marking an assignment complete and updating both completion fields.
    completion_state = State(
        [Assignment("CISC 108", "Project", "11/20/2026", None, False)],
        ["CISC 108"],
        [],
        0,
    )
    completeAssignment(completion_state, 0)
    assert_equal(completion_state.assignments[0].completed, True)
    assert_equal(len(completion_state.completed), 1)
    assert_equal(completion_state.completed_amount, 1)

    # Test that completing the same assignment again does not double-count it.
    completeAssignment(completion_state, 0)
    assert_equal(len(completion_state.completed), 1)
    assert_equal(completion_state.completed_amount, 1)

    # Test saving a valid grade and rejecting grades outside 0 to 100.
    saveGrade(completion_state, 0, 95.0)
    assert_equal(completion_state.assignments[0].grade, 95.0)
    saveGrade(completion_state, 0, 101.0)
    assert_equal(completion_state.assignments[0].grade, 95.0)
    saveGrade(completion_state, 0, -1.0)
    assert_equal(completion_state.assignments[0].grade, 95.0)

    # Test that an unfinished assignment cannot receive a grade.
    unfinished_state = State(
        [Assignment("CISC 108", "Homework", "11/21/2026", None, False)],
        ["CISC 108"],
        [],
        0,
    )
    saveGrade(unfinished_state, 0, 88.0)
    assert_equal(unfinished_state.assignments[0].grade, None)

    # Test that an invalid assignment index does not change state.
    saveGrade(completion_state, 20, 88.0)
    completeAssignment(completion_state, 20)
    assert_equal(completion_state.completed_amount, 1)

    # Test the deletion confirmation route without deleting the assignment.
    confirmation_state = State(
        [Assignment("CISC 108", "Project", "11/20/2026", 95.0, True)],
        ["CISC 108"],
        [],
        1,
    )
    confirmDelete(confirmation_state, 0)
    assert_equal(len(confirmation_state.assignments), 1)

    # Test deleting a completed assignment updates every related State field.
    confirmation_state.completed.append(confirmation_state.assignments[0])
    removeAssignment(confirmation_state, 0)
    assert_equal(len(confirmation_state.assignments), 0)
    assert_equal(len(confirmation_state.completed), 0)
    assert_equal(confirmation_state.completed_amount, 0)

    # Test deleting an unfinished assignment.
    active_state = State(
        [Assignment("CISC 108", "Homework", "11/22/2026", None, False)],
        ["CISC 108"],
        [],
        0,
    )
    removeAssignment(active_state, 0)
    assert_equal(len(active_state.assignments), 0)
    assert_equal(active_state.completed_amount, 0)

    # Test that an invalid deletion index does not remove anything.
    removeAssignment(active_state, 10)
    assert_equal(len(active_state.assignments), 0)


# Run tests before starting the website. Test variables stay local to run_tests.
run_tests()


# Start the website. Keep this as the last line of the program.
start_server(State([], [], [], 0), site_title="Student Assignment Tracker")
