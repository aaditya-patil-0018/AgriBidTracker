import sqlite3
import json
from auction import Auction
import pprint

class Farmer:

    # add farmer
    # get farmer
    # create auction
    # get auction data
    # add produce
    # update produce

    def __init__(self):
        self.dbname = "farmer.db"
        self.json_file = "farmer.json"
        self.create_table()

    def create_table(self):
        '''
            Farmer Database Attributes
                id
                fid
                name
                phone number
                email
                address
                produce list
                area
                organic
        '''
        connection = sqlite3.connect(self.dbname)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fid TEXT UNIQUE,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                produce_list TEXT,  -- JSON format
                area REAL,
                organic BOOLEAN
            )
        ''')
        connection.commit()
        connection.close()

    def add_farmer(self, name, phone, email, address, produce_list, area, organic):
        """
        Adds a new farmer to the database.
        """
        connection = sqlite3.connect(self.dbname)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM farmers')
        total_farmer = len(cursor.fetchall())
        self.fid = f"fid{total_farmer+1}"
        cursor.execute('''
            INSERT INTO farmers (fid, name, phone, email, address, produce_list, area, organic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.fid, name, phone, email, address, json.dumps(produce_list), area, organic))
        connection.commit()
        connection.close()

    def get_farmer(self, fid):
        """
        Retrieves farmer data from the database based on farmer ID.
        """
        connection = sqlite3.connect(self.dbname)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM farmers WHERE fid = ?', (fid,))
        farmer = cursor.fetchone()
        connection.close()
        return farmer

    def add_produce(self, produce_item, fid=""):
        """
        Adds a new produce item to a farmer's produce list.
        """
        if fid == "":
            farmer = self.get_farmer(self.fid)
        else:
            farmer = self.get_farmer(fid)
        if farmer:
            produce_list = json.loads(farmer[6])  # Assuming produce_list is the 7th column in the table
            produce_list[len(produce_list) + 1] = produce_item
            if fid == "":
                self.update_produce(produce_list, self.fid)
            else:
                self.update_produce(produce_list, fid)
        else:
            print("Farmer not found.")

    def update_produce(self, produce_list, fid=""):
        """
        Updates the produce list of a farmer.
        """
        connection = sqlite3.connect(self.dbname)
        cursor = connection.cursor()
        if fid == "":
            cursor.execute('''
                UPDATE farmers
                SET produce_list = ?
                WHERE fid = ?
            ''', (json.dumps(produce_list), self.fid))
            connection.commit()
            connection.close()
            self.get_farmer(self.fid)
        elif fid != "":
            cursor.execute('''
                UPDATE farmers
                SET produce_list = ?
                WHERE fid = ?
            ''', (json.dumps(produce_list), fid))
            connection.commit()
            connection.close()
            self.get_farmer(fid)

    def create_auction(self, auction_produce, auction_description, fid=""):
        # create auction
        auction = Auction()
        auction.create_auction()
        # connecting with database
        connection = sqlite3.connect(self.dbname)
        cursor = connection.cursor()
        if fid == "":
            # get all the farmers data
            cursor.execute(f"SELECT name FROM farmers WHERE fid='{self.fid}'")
        else:
            # get all the farmers data
            cursor.execute(f"SELECT name FROM farmers WHERE fid='{fid}'")
        farmer_name = cursor.fetchone()[0]
        print(farmer_name)
        # load the json file for storing auction data
        with open(self.json_file, "r") as file:
            self.json_data = json.load(file)
        auction_data = {
            "auction_id": auction.auction_id,
            "auction_produce": auction_produce,
            "auction_description": auction_description,
            "auction_status": auction.auction_status,
            "highest_bid": auction.highest_bid
        }
        if fid == "":
            # if fid is present in the auction data
            if self.fid in self.json_data:
                self.json_data[self.fid]["farmer_auction"].append(auction_data)
            # if fid is not present in the auction data, create new auction data
            else:
                self.json_data[self.fid] = {
                    "farmer_name": farmer_name,
                    "farmer_auction": [auction_data]
                }
        else:
            # if fid is present in the auction data
            if fid in self.json_data:
                self.json_data[fid]["farmer_auction"].append(auction_data)
            # if fid is not present in the auction data, create new auction data
            else:
                self.json_data[fid] = {
                    "farmer_name": farmer_name,
                    "farmer_auction": [auction_data]
                }
        # write data to the json
        with open(self.json_file, "w") as file:
            self.json_data = json.dump(self.json_data, file, indent=4)
        connection.commit()
        connection.close()
        print("Added Produce for Auction.")

    def get_auction_data(self, fid, auction_id):
        for auction_data in self.json_data[fid]["farmer_auctions"]:
            if auction_data["auction_id"] == auction_id:
                pprint(auction_data)
                return auction_data
        else:
            print("Auction data not found!")
            return False

    def update_auction_status(self, fid, auction_id, status):
        for auction_data in self.json_data[fid]["farmer_auctions"]:
            if auction_data["auction_id"] == auction_id:
                auction_data["auction_status"] = status
                print("Auction data changed!")
                return True
        else:
            return False


    def change_auction_highest_bid(self, fid, auction_id, highest_bid):
        for auction_data in self.json_data[fid]["farmer_auctions"]:
            if auction_data["auction_id"] == auction_id:
                auction_data["highest_bid"] = highest_bid
                print("Auction data changed!")
                return True
        else:
            return False

if __name__ == "__main__":
    # creating farmer object
    farmer = Farmer()

    # print the command
    print("Commands:")
    print("1️⃣   add farmer")
    print("2️⃣   get farmer")
    print("3️⃣   add produce")
    print("4️⃣   update produce")
    print("5️⃣   create auction")
    print("6️⃣   get auction")
    print("7️⃣   update auction status")
    print("8️⃣   change auction highest bid")
    
    stop = False
    while not stop:
        # enter command
        command = input("command ➡️    ")

        # if command 1 then create new farmer
        if command == "1":
            name = input("Enter farmer name: ")
            phone = input("Enter farmer phone number: ")
            email = input("Enter farmer email id: ")
            address = input("Enter farmer address: ")
            produce_list = {}
            add_more = True
            while add_more:
                do_you_want_to_add_more = input("Do you want to add more? [y/n]: ")
                if do_you_want_to_add_more == "y":
                    produce_list[len(produce_list) + 1] = input("Enter the name of produce that you are growing: ")
                else:
                    add_more = False
            area = input("What the area of your farm: ")
            organic = input("Do you follow organic practices? [y/n] : ")
            farmer.add_farmer(name, phone, email, address, produce_list, area, organic)
        
        # if command 2 get the farmer details and print it
        elif command == "2":
            farmer_id = input("Ente farmer id of the farmer to get the data: ")
            farmer.get_farmer(farmer_id)

        # if command 3 then add produce within the farmer details
        elif command == "3":
            exisiting = input("Do you have farmer id? [y/n]: ")
            if exisiting == "n":
                produce = input("Enter produce name to add: ")
                farmer.add_produce(produce)
            else:
                farmer_id = input("Enter farmer id: ")
                produce = input("Enter produce name to add: ")
                farmer.add_produce(produce_item=produce, fid=farmer_id)
        
        # updating produce farmer details
        elif command == "4":
            print("Choose other...")

        # if command 5 then create auction under farmer's name
        elif command == "5":
            farmer_id = input("Enter farmer id: ")
            auction_produce = input("Enter the produce you want to add for auction: ")
            auction_description = input("Enter your auction description: ")
            farmer.create_auction(auction_produce, auction_description, farmer_id)
        
        # if command 6 then get the data of the auction under the farmers id
        elif command == "6":
            farmer_id = input("Enter farmer id: ")
            auction_id = input("Enter your auction_id: ")
            farmer.get_auction_data(farmer_id, auction_id)
        
        # if command 7 then update the status of the auction within the farmers id
        elif command == "7":
            farmer_id = input("Enter farmer id: ")
            auction_id = input("Enter your auction_id: ")
            status = input("Enter auction status: ")
            farmer.update_auction_status(farmer_id, auction_id, status)
        
        # if command 8 then update the highest bid of the auction within the farmers id
        elif command == "8":
            farmer_id = input("Enter farmer id: ")
            auction_id = input("Enter your auction_id: ")
            highest_bid = input("Enter auction highest bid: ")
            farmer.change_auction_highest_bid(farmer_id, auction_id, highest_bid)

        # else stop the loop
        else:
            stop = True
            print("Stop the program!")
