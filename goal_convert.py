
# Creates the contents and sorts the formatting
def goal_convert(content, goal_list):
    del content["submit"]
    del content["goals[]"]
    content['exercise_type'] = content["exercise_type"].lower()

    goal_string = goal_list[0]

    while "" in goal_list:
        goal_list.remove("")

    # Only when there is more than one goal will commas be added.
    if len(goal_list) > 1:
        goal_string = ", ".join(goal_list)
        if goal_string[-2:] == ", ":
            goal_string = goal_string[:-2]

    content['goals'] = goal_string

    return content
