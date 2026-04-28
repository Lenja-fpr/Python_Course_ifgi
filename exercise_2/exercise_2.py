# donuts

# Given an integer count of a number of donuts, return a string
# of the form 'Number of donuts: <count>', where <count> is the number
# passed in. However, if the count is 10 or more, then use the word 'many'
# instead of the actual count.
# So donuts(5) returns 'Number of donuts: 5'
# and donuts(23) returns 'Number of donuts: many'
#def donuts(count):
# +++ your code here +++
#return


# verbing

# Given a string, if its length is at least 3,
# add 'ing' to its end.
# Unless it already ends in 'ing', in which case
# add 'ly' instead.
# If the string length is less than 3, leave it unchanged.
# Return the resulting string.
# def verbing(s):
# +++your code here+++
# return


# Remove adjacent

# Given a list of numbers, return a list where
# all adjacent == elements have been reduced to a single element,
# so [1, 2, 2, 3] returns [1, 2, 3]. You may create a new list or
# modify the passed in list.
def remove_adjacent(nums):
    
    # create a list for the reduced version of nums
    reducedNums = []

    # for every element in nums
    for i in nums:

        # set isInReducedNums to False
        isInReducedNums = False

        # for every element in reducedNums:
        for j in reducedNums:
            # if the element from nums already in the reducedNums list, set isInReducedNums to True
            if i == j:
                isInReducedNums = True

        # if the element is not in the reducedNums list, add it to the list
        if isInReducedNums == False:
            reducedNums.append(i)

    # return the reduced version of the list
    return reducedNums



def main():
    #print('donuts')
    #print(donuts(4))
    #print(donuts(9))
    #print(donuts(10))
    #print(donuts('twentyone'))

    #print('verbing')
    #print(verbing('hail'))
    #print(verbing('swiming'))
    #print(verbing('do'))

    print('remove_adjacent')
    print(remove_adjacent([1, 2, 2, 3]))
    print(remove_adjacent([2, 2, 3, 3, 3]))
    print(remove_adjacent([]))

# Standard boilerplate to call the main() function.
if __name__ == '__main__':
    main()