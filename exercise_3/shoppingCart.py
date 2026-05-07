class shoppingCart:

    def __init__(self):
        self.items = []

    def addItem(self, item, quantity):
        self.items.append([item, quantity])

    def removeItem(self, item):
        c = 0
        toDelete = []

        while c < len(self.items):
            if self.items[c][0] == item:
                toDelete.append(c)
            c = c+1

        d = len(toDelete) - 1
        
        while d >= 0:
            del self.items[toDelete[d]]
            d = d - 1

    def calculateTotalItems(self):
        
        numberOfItems = 0

        for item in self.items:
            numberOfItems = numberOfItems + item[1]
    
        return numberOfItems

    
