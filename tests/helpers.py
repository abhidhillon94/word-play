def are_lists_of_dicts_equal(list1, list2):

    # Check if the lists have the same length
    if len(list1) != len(list2):
        return False
    
    # Create a copy of the lists to avoid modifying the original ones
    list1_copy = list(list1)
    list2_copy = list(list2)
    
    # Iterate over the dictionaries in list1
    for dict1 in list1:
        # Check if dict1 exists in list2
        if dict1 in list2_copy:
            # Remove the matching dictionary from list2_copy
            list2_copy.remove(dict1)
        else:
            return False
    
    # If all dictionaries in list1 have been found in list2, the lists are the same
    return True