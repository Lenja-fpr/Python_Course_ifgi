# donuts

# Given an integer count of a number of donuts, this function returns a string
# of the form 'Number of donuts: <count>', where <count> is the number
# passed in. However, if the count is 10 or more, then the word 'many' is used
# instead of the actual count.
def donuts(count):
    if type(count) != int:
        return(str(count) + ' is not an integer')
    if int(count) < 10:
        return('Number of donuts: ' + str(count))
    return('Number of donuts: many')


# verbing

# Given a string, if its length is at least 3, this function adds 'ing' to its end,
# unless it already ends in 'ing', in which case 'ly' is added instead.
# If the string length is less than 3, it is left unchanged.
# Returns the resulting string.
def verbing(s):
    if type(s) != str:
        return(str(s) + ' is not a string')
    if len(s) < 3:
        return(s)
    if s[-3:] == 'ing':
        return(s + 'ly')
    return(s + 'ing')


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
    print('donuts')
    print(donuts(4))
    print(donuts(9))
    print(donuts(10))
    print(donuts('twentyone'))

    print('verbing')
    print(verbing('hail'))
    print(verbing('swiming'))
    print(verbing('do'))

    print('remove_adjacent')
    print(remove_adjacent([1, 2, 2, 3]))
    print(remove_adjacent([2, 2, 3, 3, 3]))
    print(remove_adjacent([]))

# Standard boilerplate to call the main() function.
if __name__ == '__main__':
    main()