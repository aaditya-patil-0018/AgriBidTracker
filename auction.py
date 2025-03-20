import json
import uuid
from pprint import pprint

class Auction:

    def __init__(self, auction_id=""):
        self.json_file = "auction_data.json"
        if auction_id != "":
            self.auction_id = auction_id
            self.get_auction_data()
            self.auction_status = self.data[auction_id]['status']
        else:
            self.get_auction_data()
        # pprint(self.data)

    def get_auction_data(self, auction_id=""):
        with open(self.json_file, 'r') as file:
            self.data = json.load(file)
        if auction_id != "":
            pprint(self.data[auction_id])
            return self.data[auction_id]
        else:
            return self.data

    def update_auction_data(self):
        with open(self.json_file, 'w') as file:
            json.dump(self.data, file, indent=4)
        self.get_auction_data()

    def create_auction(self, bidstart=0):
        all_auction_id = self.get_all_auction_id()
        uuid_assigned = False
        while uuid_assigned == False:
            self.auction_id = str(uuid.uuid4())
            if self.auction_id not in all_auction_id:
                uuid_assigned = True
        self.auction_status = "opened"
        self.number_of_bidders = 0
        self.highest_bid = 0
        self.data[self.auction_id] = {
            "status": self.auction_status,
            "highest_bid": bidstart,
            "highest_bid_id": "",
            "bidder_details": {},
            "bidding_details": {}
        }
        self.update_auction_data()
        return self.auction_id

    def get_all_auction_id(self):
        all_auction_id = []
        for auction_id in self.data:
            all_auction_id.append(auction_id)
        return all_auction_id

    def add_bidder(self, merchant_id):
        if self.data[self.auction_id]["status"] == "opened":
            self.data[self.auction_id]["bidder_details"][merchant_id] = []
            self.update_auction_data()
        else:
            print(f"Auction {self.auction_id} status is {self.auction_status}")
    
    def bid_up(self, merchant_id, amount):
        if self.data[self.auction_id]["status"] == "opened":
            # checking for new highest condition
            current_highest = self.data[self.auction_id]["highest_bid"]
            if int(current_highest) < int(amount):
                # setting highest bid data
                self.data[self.auction_id]["highest_bid"] = amount
                self.highest_bid = amount
                self.data[self.auction_id]["highest_bid_id"] = merchant_id
                # adding the new bid to the auction
                srno = len(self.data[self.auction_id]["bidding_details"]) + 1
                self.data[self.auction_id]["bidding_details"][srno] = {
                    "merchant_id": merchant_id,
                    "bid": amount
                }
                # adding new bid in merchant (bidder) data
                self.data[self.auction_id]["bidder_details"][merchant_id].append(amount)
                self.update_auction_data()
                return [True]
            else:
                msg = "Amount should be greater than last bidding amount!"
                print(msg)
                return [False, msg]
        else:
            msg = f"Auction {self.auction_id} status is {self.auction_status}"
            print(msg)
            return [False, msg]

    def close_auction(self):
        self.auction_status = "closed"

if __name__ == "__main__":
    auction = Auction()
    print("➡️   Command")
    print("1️⃣   Create Auction")
    print("2️⃣   Add Bidder")
    print("3️⃣   Bid")
    print("4️⃣   Get Auction Data")
    print("🛑   Stop: `stop` ")
    stop = False
    while not stop:
        command = input("command ➡️   ")
        if command == '1':
            create = input("create [y/n] ➡️  ")
            if create == "y":
                auction.create_auction()
            else:
                auction_id = input("Enter auction id ➡️  ")
                auction = Auction(auction_id=auction_id)
        elif command == '2':
            merchant_id = input("Enter merchant id ➡️   ")
            auction.add_bidder(merchant_id=merchant_id)
        elif command == '3':
            merchant_id = input("Enter merchant id ➡️   ")
            amount = input("Enter amount for bidding ➡️   ")
            auction.bid_up(merchant_id=merchant_id, amount=amount)
        elif command == '4':
            auction.get_auction_data(auction_id=auction.auction_id)
        else:
            stop = True