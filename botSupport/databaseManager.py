import sqlite3 as sqlite
from typing import Optional
import random

class Loot:
    Name: str
    Description: str
    Consumable: bool
    attackRarity: int
    vcRarity: int

    def __init__(self, name, description, consumable, attackRarity, vcRarity) -> None:
        self.Name = name
        self.Description = description
        self.Consumable = consumable
        self.attackRarity = attackRarity
        self.vcRarity = vcRarity

    def __str__ (self) -> str:
        return f"Name: {self.Name}, Description: {self.Description}, Consumable: {self.Consumable}, attackRarity: {self.attackRarity}, vcRarity: {self.vcRarity}"
    def __repr__(self) -> str:
        return f"Loot({self.Name}, {self.Description}, {self.Consumable}, {self.attackRarity}, {self.vcRarity})"
    
    def __eq__(self, other):
        return self.Name == other.Name
    def __hash__(self) -> int:
        return hash(self.Name)

class User:
    UserID:int
    AmountOfDeaths:int
    Health:int
    Inventory: dict[Loot: int]
    Strength: int
    Dexterity: int
    Intelligence: int
    Charisma: int

    def __init__(self, userID, amountOfDeaths, health, inventory, strength, dexterity, intelligence, charisma) -> None:
        self.UserID = userID
        self.AmountOfDeaths = amountOfDeaths
        self.Health = health
        self.Inventory = inventory
        self.Strength = strength
        self.Dexterity = dexterity
        self.Intelligence = intelligence
        self.Charisma = charisma

    def __str__(self) -> str:
        return f"UserID: {self.UserID}, AmountOfDeaths: {self.AmountOfDeaths}, Health: {self.Health}, Loot: {self.Inventory}, Strength: {self.Strength}, Dexterity: {self.Dexterity}, Intelligence: {self.Intelligence}, Charisma: {self.Charisma}"
    def __repr__(self) -> str:
        return f"User({self.UserID}, {self.AmountOfDeaths}, {self.Health}, {self.Inventory}, {self.Strength}, {self.Dexterity}, {self.Intelligence}, {self.Charisma})"
    
    def __eq__(self, other):
        return self.UserID == other.UserID

class Attack:
    AttackID: int
    AttackingUser: User
    DefendingUser: User
    Type: str
    Description: str
    Complete: bool
    Winner: User

    def __init__(self, attackID, attackingUser, defendingUser, Type, attackDescription, Complete, Winner) -> None:
        self.AttackID = attackID
        self.AttackingUser = attackingUser
        self.DefendingUser = defendingUser
        self.Type = Type
        self.Description = attackDescription
        self.Complete = Complete
        self.Winner = Winner

    def __str__(self) -> str:
        return f"AttackID: {self.AttackID}, AttackingUser: {self.AttackingUser}, DefendingUser: {self.DefendingUser}, Type: {self.Type}, Description: {self.Description}, Complete: {self.Complete}, Winner: {self.Winner}"
    def __repr__(self) -> str:
        return f"Attack({self.AttackID}, {self.AttackingUser}, {self.DefendingUser}, {self.Type}, {self.Description}, {self.Complete}, {self.Winner})"
    
    def __eq__(self, other):
        return self.AttackID == other.AttackID

class DatabaseManager:
    def __init__(self):
        self.connection = sqlite.connect("database.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS User (UserID INTEGER PRIMARY KEY, AmountOfDeaths INTEGER DEFAULT 0, Health INTEGER DEFAULT 3, Strength INTEGER, Dexterity INTEGER, Intelligence INTEGER, Charisma INTEGER);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS UserLoot(UserID INTEGER PRIMARY KEY, FOREIGN KEY (UserID) REFERENCES User(UserID));")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Attack (AttackID INTEGER PRIMARY KEY, AttackingUserID INTEGER, DefendingUserID INTEGER, Type TEXT, Description TEXT, Complete BOOLEAN DEFAULT False, Winner TEXT DEFAULT NULL, FOREIGN KEY (AttackingUserID) REFERENCES User(UserID), FOREIGN KEY (DefendingUserID) REFERENCES User(UserID))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Loot (LootName TEXT PRIMARY KEY, LootDescription TEXT, Consumable BOOLEAN, attackRarity INTEGER, vcRarity INTEGER)")
        implementedLoot = (
            ("Gold", "Is shiny", False, "70", "0"), 
            ("Health Potion", "Adds 1 Health", True, "33", "20"), 
            ("Steroids", "Adds 1 Strength", True, "20", "15"), 
            ("Weed", "Adds 1 Charisma", True, "20", "15"), 
            ("Shrooms", "Adds 1 Intelligence", True, "20", "15"), 
            ("Potion of Swiftness", "Adds 1 Dexterity", True, "20", "15"), 
            ("Totem of Undying", "When you die the totem takes your place", False, "10", "10"), 
            ("Forcefield", "You won't take damage the next time you are hit", False, "5", "5")
        )
        self.cursor.executemany("INSERT OR IGNORE INTO Loot (LootName, LootDescription, Consumable, attackRarity, vcRarity) VALUES (?, ?, ?, ?, ?)", implementedLoot)
        for lootType in implementedLoot:
            self.cursor.execute(f"PRAGMA table_info(UserLoot)")
            columns = [row[1] for row in self.cursor.fetchall()]
            if lootType[0] not in columns:
                self.cursor.execute(f"ALTER TABLE UserLoot ADD `{lootType[0]}` INTEGER DEFAULT 0")
        self.connection.commit()
        

    def __del__(self):
        self.connection.close()

    def getAttacks(self) -> list[Attack]:
        response = self.cursor.execute("SELECT * FROM Attack").fetchall()
        attacks = []
        for attack in response:
            attacks.append(Attack(attack[0], self.getUser(attack[1]), self.getUser(attack[2]), attack[3], attack[4], attack[5], self.getUser(attack[6])))
        return attacks


    def getUser(self, userID: int) -> User:
        if userID == None:
            return None
        response = self.cursor.execute(f"SELECT * FROM User JOIN UserLoot ON User.UserID = UserLoot.UserID WHERE User.UserID = {userID} ").fetchall()
        if response == []:
            self.cursor.execute(f"INSERT INTO User (UserID, Strength, Dexterity, Intelligence, Charisma) VALUES ({userID}, {random.randint(1, 10)}, {random.randint(1, 10)}, {random.randint(1, 10)}, {random.randint(1, 10)})")
            self.cursor.execute(f'INSERT INTO UserLoot (UserID) VALUES ({userID})')
            self.connection.commit()
            response = self.cursor.execute(f"SELECT * FROM User JOIN UserLoot ON User.UserID = UserLoot.UserID WHERE User.UserID = {userID} ").fetchall()
        
        # construct the loot tuple object called userLoot
        columnData = self.cursor.execute("PRAGMA table_info(UserLoot)").fetchall()
        
        lootList = []
        for i, row in enumerate(columnData):
            if i == 0:
                continue
            for lootType in self.getLootTable():
                if lootType.Name == row[1]:
                    lootList.append(lootType)

        userLoot = {}
        for i, loot in enumerate(lootList, 8):
            amount = response[0][i]
            if amount != 0:
                userLoot.update({loot: amount})
        
        user = User(response[0][0], response[0][1], response[0][2], userLoot, response[0][3], response[0][4], response[0][5], response[0][6])
        return user
    
    def createAttack(self, attackingUser: User, defendingUser: User, Type: str, attackDescription: str) -> Attack:
        self.cursor.execute(f"INSERT INTO Attack (AttackingUserID, DefendingUserID, Type, Description) VALUES (?, ?, ?, ?)", (attackingUser.UserID, defendingUser.UserID, Type, attackDescription))
        self.connection.commit()
        return self.getAttack(self.cursor.lastrowid)
    
    def editAttack(self, attack: Attack, Type: str, attackDescription: Optional[str], Winner: Optional[User]):
        if attackDescription:
            attackDescription = attackDescription.replace("'", "\\'")
            self.cursor.execute(f"UPDATE Attack SET Type = '{Type}', Description = '{attackDescription}' WHERE AttackID = {attack.AttackID}")
        if Winner:
            self.cursor.execute(f"UPDATE Attack SET Winner = {Winner.UserID} WHERE AttackID = {attack.AttackID}")
        self.connection.commit()

    def completeAttack(self, attack: Attack, winner: User): 
        self.cursor.execute(f"UPDATE Attack SET Complete = True WHERE AttackID = {attack.AttackID}")
        if winner:
            self.cursor.execute(f"UPDATE Attack SET Winner = {winner.UserID} WHERE AttackID = {attack.AttackID}")
        self.connection.commit()
    
    def getAttack(self, attackID: int) -> Attack:
            for attack in self.getAttacks():
                if attack.AttackID == attackID:
                    return attack

    def getLootTable(self) -> list[Loot]:
        lootList = []
        response = self.cursor.execute("SELECT * FROM Loot").fetchall()
        
        for row in response:
            lootList.append(Loot(row[0], row[1], row[2], row[3], row[4]))

        return lootList
    
    def editRarity(self, lootName: str, attackRarity: int, vcRarity: int):
        self.cursor.execute(f"UPDATE Loot SET attackRarity = {attackRarity}, vcRarity = {vcRarity} WHERE LootName = '{lootName}'")
        self.connection.commit()
    
    def updateHealth(self, user: User, newhealth: int):
        self.cursor.execute(f"UPDATE User SET Health = {newhealth} WHERE UserID = {user.UserID}")
        self.connection.commit()
    
    def updateDeaths(self, user: User, newDeaths: int):
        self.cursor.execute(f"UPDATE User SET AmountOfDeaths = {newDeaths} WHERE UserID = {user.UserID}")
        self.connection.commit()

    def giveLoot(self, user: User, lootList: dict[Loot: int]) -> User:
        for loot, amount in lootList.items():
            newAmount = user.Inventory.get(loot) + amount
            self.cursor.execute(f'UPDATE UserLoot SET \'{loot.Name}\' = {newAmount} WHERE UserID = {user.UserID}')
        self.connection.commit()
        return self.getUser(user.UserID)

    def removeLoot(self, user: User, lootToRemove: Loot):
        newValue = user.Inventory.get(lootToRemove) - 1
        self.cursor.execute(f'UPDATE UserLoot SET \'{lootToRemove.Name}\' = {newValue}')
        self.connection.commit()

    def addLootType(self, lootName: str, lootDescription: str, consumable: bool, attackRarity: int, vcRarity: int):
        self.cursor.execute(f"INSERT INTO Loot (LootName, LootDescription, Consumable, attackRarity, vcRarity) VALUES (?, ?, ?, ?, ?)", (lootName, lootDescription, consumable, attackRarity, vcRarity))
        self.cursor.execute(f"ALTER TABLE UserLoot ADD '{lootName}' INTEGER DEFAULT 0")
        self.connection.commit()

    def useLoot(self, user: User, lootToRemove: Loot) -> User:
        newValue = user.Inventory.get(lootToRemove) - 1

        lootList: list[Loot] = self.getLootTable()
        if lootToRemove == lootList[0]: #Gold
            return
        
        self.cursor.execute(f'UPDATE UserLoot SET \'{lootToRemove.Name}\' = {newValue}')
        if lootToRemove == lootList[1]: #Health Potion
            self.updateHealth(user, user.Health + 1)
        elif lootToRemove == lootList[2]: #Steroids
            self.updateUserStats(user, strength = user.Strength + 1)
        elif lootToRemove == lootList[3]: #Weed
            self.updateUserStats(user, charisma = user.Charisma + 1)
        elif lootToRemove == lootList[4]: #Shrooms
            self.updateUserStats(user, intelligence = user.Intelligence + 1)
        elif lootToRemove == lootList[5]: #Potion of Swiftness
            self.updateUserStats(user, dexterity = user.Dexterity + 1)
        else:
            raise NotImplementedError(f'{lootToRemove.Name} is not implemented')
        
        return self.getUser(user.UserID)

    def updateUserStats(self, user: User, strength: int = None, dexterity: int = None, intelligence: int = None, charisma: int = None):
        if strength:
            self.cursor.execute(f"UPDATE User SET Strength = {strength} WHERE UserID = {user.UserID}")
        if dexterity:
            self.cursor.execute(f"UPDATE User SET Dexterity = {dexterity} WHERE UserID = {user.UserID}")
        if intelligence:
            self.cursor.execute(f"UPDATE User SET Intelligence = {intelligence} WHERE UserID = {user.UserID}")
        if charisma:
            self.cursor.execute(f"UPDATE User SET Charisma = {charisma} WHERE UserID = {user.UserID}")
        self.connection.commit()

    def reset(self):
        self.cursor.execute("DROP TABLE User")
        self.cursor.execute("DROP TABLE UserLoot")
        self.cursor.execute("DROP TABLE Attack")
        self.cursor.execute("DROP TABLE Loot")
        

if __name__ == "__main__":
    db = DatabaseManager()
    # print(db.cursor.execute("SELECT * FROM User").fetchall())
    # print(db.getUser(1))
    # for item in db.getUser(1).Inventory.items():
    #     print(item.Name)
    # print(db.getUser(875963554803646514))
    # db.addLootType("Health Potion", "Adds 1 health", 70, 10)
    # db.addLootType("Poison Potion", "Removes 1 health", 70, 10)
    # db.addLootType("Gold", "is shiny", 50, 0)
    # print(db.getLootTable())
    # db.updateDeaths(db.getUser(244163818782064641), 1)
    # loot = db.getLootTable()[0]
    # db.giveLoot(db.getUser(336959815374864384), {loot: 1})
    # db.giveLoot(db.getUser(1), [(db.getLootTable()[0], 2)])
    # print(db.getUser(1))
    # print(db.createAttack(attackingUser=db.getUser(875963554803646514), defendingUser=db.getUser(336959815374864384), Type="Single Target", attackDescription="CHAIR"))
    # print(db.getAttacks())
    # db.completeAttack(db.getAttack(13), None)
    # attacks = db.getAttacks()
    # print(1 in attacks[*][1])
    # db.removeLoot(db.getUser(1), db.getLootTable()[0])
    # print(db.cursor.execute(f"UPDATE User SET Health = {2} WHERE UserID = {1}"))
    # for attack in db.getAttacks():
        # db.completeAttack(attack)
    # print(db.getUser(1))
    db.connection.close()
