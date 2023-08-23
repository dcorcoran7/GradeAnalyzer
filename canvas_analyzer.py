"""
Project 6
Canvas Analyzer
CS 1064 Introduction to Programming in Python
Spring 2018

Access the Canvas Learning Management System and process learning analytics.

Edit this file to implement the project.
To test your current solution, run the `test_my_solution.py` file.
Refer to the instructions on Canvas for more information.

"I have neither given nor received help on this assignment."
author: David Corcoran
"""
__version__ = 7

import matplotlib.pyplot as plt
import canvas_requests
import datetime


# 1) main
"""Consumes: user
Calls all following funcions in the correct order"""
def main(user_id):
    user_dictionary = canvas_requests.get_user(user_id)
    print_user_info(user_dictionary)
    courses = canvas_requests.get_courses(user_id)
    courses_dictionary = filter_available_courses(courses)
    print_courses(courses_dictionary)
    course_id_list = get_course_ids(courses_dictionary)
    chosen_course_id = choose_course(course_id_list)
    submissions = canvas_requests.get_submissions(user_id, chosen_course_id)
    summarize_points(submissions)
    summarize_groups(submissions)
    plot_scores(submissions)
    plot_grade_trends(submissions)
    
# 2) print_user_info
"""Consumes: user_dictionary
Prints the name, title, email, and bio of the user"""
def print_user_info(user_dictionary):
    print("Name: " + user_dictionary["name"])
    print("Title: " + user_dictionary["title"])
    print("Primary Email: " + user_dictionary["primary_email"])
    print("Bio: " + user_dictionary["bio"])

# 3) filter_available_courses
"""Consumes: courses, a list of dictionaries
Returns a list of courses with the workflow as available
"""
def filter_available_courses(courses):
    course_list = []
    for course in courses:
        if course["workflow_state"] == "available":
            course_list.append(course)
    return course_list

# 4) print_courses
"""Consumes: courses_dictionary, the output of the previous function
Prints the course id and name of the courses found as available
"""
def print_courses(courses_dictionary):
    for course in courses_dictionary:
        print(str(course["id"]) + " : " + course["name"])

# 5) get_course_ids
"""Consumes: courses_dictionary, a list of dicitonaries for the coureses available
Returns a list of inteers representing the ids for the available courses
"""
def get_course_ids(courses_dictionary):
    list_of_integers =[]
    for course in courses_dictionary:
        list_of_integers.append(course["id"])
    return list_of_integers

# 6) choose_course
"""Consumes: coure_id_list, a list of ids for available courses
Returns the choice that the user inputs as the id they wish to lookup
"""
def choose_course(course_id_list):
    choice_parameter = True
    print(course_id_list)
    while choice_parameter == True:
        id_choice = input("Enter a valid course ID")
        if int(id_choice) in course_id_list:
            choice_parameter = False
            return int(id_choice)
   
# 7) summarize_points
"""Consumes: submissions, a list of dictionaries for submitted assignments
Prints points available so far, points obtained by the user, and the current grade of theuser by dividing points available and points obtained and multiplying by 100
"""
def summarize_points(submissions):
    points_possible_so_far = 0
    points_obtained = 0
    for submission in submissions:
        if submission["score"] != None:
            points_possible_so_far += submission["assignment"]["points_possible"] * submission["assignment"]["group"]["group_weight"]
    print("Points Possible So Far: " + str(points_possible_so_far))
    for submission in submissions:
        if submission["score"] != None:
            points_obtained += submission["score"] * submission["assignment"]["group"]["group_weight"]
    print("Points Obtained: " + str(points_obtained))
    print("Current Grade: " + str(round((points_obtained / points_possible_so_far) * 100)))
    
# 8) summarize_groups
"""Consumes: submissions, a list of dictionaries for submitted assignments
Prints the unweighted grade foe ach assignent groups (category) by dividing the accumualted score by the accumulated points possible in each group
"""
def summarize_groups(submissions):
    types = {}
    for submission in submissions:
        if submission["score"] != None:
            category = submission["assignment"]["group"]["name"]
            if category in types:
                types[category][0] += submission["assignment"]["points_possible"]
                types[category][-1] += submission["score"]
            else:
                types[category] = [submission["assignment"]["points_possible"], submission["score"]]
    for location in types:
        print("* " + str(location) + ": " + str(round((types[location][-1] / types[location][0]) * 100)))
    
# 9) plot_scores
"""Consumes: submissions, a list of dictionarise for submitted assignments
Plots a histogram of submitted assignemnts with grades on the x axis and the number of assignment on the y axis
"""
def plot_scores(submissions):
    scores = []
    for submission in submissions:
        if submission["score"] != None and submission["assignment"]["points_possible"] > 0:
            scores.append((submission["score"] * 100) / submission["assignment"]["points_possible"])
    plt.hist(scores, edgeColor = "black")
    plt.title("Distribution of Grades")
    plt.xlabel("Grades")
    plt.ylabel("Number of Assignments")
    plt.show()
    
# 10) plot_grade_trends
"""Consumes: submissions, a list of dictionarise for submitted assignments
Plots a line graph of the users current, past, and future grade distribution by taking in running sums. It takes  running sum of three
possible outcomes: getting all assignments perfect for a mximum grade, getting all future assignments correct, and not submitting any more
assignments for the minimum grade.
"""
def plot_grade_trends(submissions):
    highest = []
    most = []
    least= []
    assignment_dates = []
    for submission in submissions:
        assignment_dates.append(datetime.datetime.strptime(submission["assignment"]["due_at"], "%Y-%m-%dT%H:%M:%SZ"))
    for submission in submissions:
        highest.append((submission["assignment"]["points_possible"] * submission["assignment"]["group"]["group_weight"]) * 100)
    highest_sum = sum(highest)
    absolute_max = highest_sum / 100
    for submission in submissions:
        if submission["workflow_state"] == "graded":
            most.append((submission["assignment"]["group"]["group_weight"] * submission["score"]) * 100)
            least.append((submission["assignment"]["group"]["group_weight"] * submission["score"]) * 100)
        else:
            most.append((submission["assignment"]["group"]["group_weight"] * submission["assignment"]["points_possible"]) * 100)
            least.append(0)
    for item in range(1, len(highest)):
        highest[item] = (highest[item - 1] + highest[item])
    for item in range(1, len(most)):
        most[item] = (most[item - 1] + most[item])
    for item in range(1, len(least)):
        least[item] = (least[item - 1] + least[item])
    rounded_highest = []
    rounded_most = []
    rounded_least = []
    for item in highest:
        rounded_highest.append(round(item / absolute_max, 2))
    for item in most:
        rounded_most.append(round(item / absolute_max, 2))
    for item in least:
        rounded_least.append(round(item / absolute_max, 2))
    
    plt.plot(assignment_dates, rounded_highest, label = "Maximum") 
    plt.plot(assignment_dates, rounded_most, label = "Highest")
    plt.plot(assignment_dates, rounded_least, label = "Lowest")
    plt.title("Grade Trend")
    plt.ylabel("Grade")
    plt.legend()
    plt.show()
    
    
# Keep any function tests inside this IF statement to ensure
# that your `test_my_solution.py` does not execute it.
if __name__ == "__main__":
    main('hermione')
    # main('ron')
    # main('harry')
    
    # https://community.canvaslms.com/docs/DOC-10806-4214724194
    # main('YOUR OWN CANVAS TOKEN (You know, if you want)')