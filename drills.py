class Store:
    def __init__(self, name):
        # You'll need 'name' as an argument to this method.
        # Then, initialise 'self.name' to be the argument, and 'self.items' to be an empty list.
        self.name = name
        self.items = []

    def add_item(self, name, price):
        # Create a dictionary with keys name and price, and append that to self.items.
        item_dict = {}
        item_dict[name] = price
        print('adding item to items list')
        self.items.append(item_dict)

    def stock_price(self):
        # Add together all item prices in self.items and return the total.
        price_sum = 0
        for item in self.items:
            print('item:', item)
            item_key = list(item.keys())[0]
            price_sum += item[item_key]
        return price_sum


stock = Store('shefa')
stock.add_item('milk', 10)
stock.add_item('chocolate', 15)
print(stock.stock_price())
