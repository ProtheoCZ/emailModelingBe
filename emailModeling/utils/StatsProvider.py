def get_children_stats(number_of_children, log_to_file=False):
    total = sum(number_of_children)
    for idx, n in enumerate(number_of_children):
        if log_to_file:
            pass  # todo logging to file
        elif idx == len(number_of_children) - 1:
            print(str(n) + ' out of ' + str(total) + ' nodes had ' + str(idx) + '+ children')
        else:
            print(str(n) + ' out of ' + str(total) + ' nodes had ' + str(idx) + ' children')  # todo add percentage
