import mysql.connector
from mysql.connector import Error, connect
from mysql.connector import IntegrityError
from os import environ as env


class WaifuBotDB:
    def __init__(self) -> None:
        self.host = env.get("DB_HOST")
        self.user = env.get("DB_USER")
        self.pw   = env.get("DB_PW")
        self.db   = env.get("DB")

        self.connection = None
        self.cursor = None
        self.response = []

        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host, user=self.user, passwd=self.pw, database=self.db)

            print(f"[DB] Connected to {self.host} as {self.user}.")

        except Error as err:
            print(f"[DB] Error: '{err}'")
            return

        self.cursor = self.connection.cursor()

    def close_connection(self):
        pass
        """
        self.cursor.close()
        self.connection.close()
        print(f"[DB] Connection to {self.host} closed!")
        """

    def execute_query(self, query):
        #self.connect()

        if self.connection == None:
            return False

        try:
            self.cursor.execute(query)
        except IntegrityError as err:
            print("[DB] Integrity Error:", err)
            self.close_connection()
            return False
        except Error as err:
            print("[DB] Unknown Error:", err)
            self.close_connection()
            return False
            
        self.response = []
        for row in self.cursor:
            self.response.append(row)
        
        self.connection.commit()
        self.close_connection()

        if len(self.response) > 0:
            return True

        if self.cursor.rowcount == 0:
            #print("[DB] No rows affected!")
            return False

        else:
            return True      


    # User
    def add_user(self, id, name, tag, avatarURL=""):
        query = "INSERT INTO User (DiscordID, UserName, Discriminator, AvatarURL) "
        query+=f"VALUES ({id}, '{name}', {tag}, '{avatarURL}');"

        if self.execute_query(query):
            print(f"[DB] User {name}#{tag} was added to the database!")
        return

    def get_user(self, id):
        query = f"SELECT * FROM User WHERE DiscordID={id};"
        if self.execute_query(query) and len(self.response):
            return True
        else:
            return False


    # Moderation
    def is_moderator(self, userID, guildID):
        query = f"SELECT * FROM Moderator WHERE UserID={userID} AND GuildID={guildID};"
        if self.execute_query(query) and len(self.response) > 0:
            print(self.response)
            return True
        else:
            return False 

    def add_moderator(self, userID, guildID):
        query = f"INSERT INTO Moderator VALUES ({userID}, {guildID});"
        if self.execute_query(query):
            print(f"[DB] Moderator {userID} of guild {guildID} was added to the database!")
            return True
        else:
            return False

    def remove_moderator(self, userID, guildID):
        query = f"DELETE FROM Moderator WHERE UserID={userID} AND GuildID={guildID};"

        if self.execute_query(query):
            print(f"[DB] Moderator {userID} of guild {guildID} was removed from the database!")
            return True
        else:
            return False

    def add_activeChannel(self, guildID, channelID):
        query = "INSERT INTO ActiveChannel (GuildID, ChannelID) "
        query+=f"VALUES ({guildID}, {channelID});"

        if self.execute_query(query):
            print(f"[DB] Channel {channelID} of guild {guildID} was added to the database!")
            return True
        else:
            return False

    def remove_activeChannel(self, channelID):
        query = f"DELETE FROM ActiveChannel WHERE ChannelID={channelID};"
        if self.execute_query(query):
            print(f"[DB] Channel {channelID} removed from database.")
            return True
        else: 
            return False

    # Waifu
    def add_activeWaifu(self, waifuID, channelID, messageID):
        query = f"INSERT INTO ActiveWaifu VALUES ({channelID}, {waifuID}, {messageID}, SYSDATE());"
        if self.execute_query(query):
            print(f"[DB] Waifu {waifuID} in channel {channelID} was added to ActiveWaifus with message {messageID}!")
            return True
        else:
            return False

    def remove_activeWaifu(self, channelID):
        query = f"DELETE FROM ActiveWaifu WHERE ChannelID={channelID};"
        if self.execute_query(query):
            print(f"[DB] Waifu from channel {channelID} was removed from ActiveWaifus!")
            return True
        else:
            return False

    def get_activeWaifu(self, channelID):
        query = f"SELECT * FROM ActiveWaifu WHERE ChannelID={channelID};"
        if self.execute_query(query):
            return True
        else:
            return False

    def get_waifu(self, waifuID):
        query = f"SELECT * FROM Waifu WHERE ID={waifuID};"
        if self.execute_query(query) and len(self.response):
            return True
        else:
            return False

    def add_haremContract(self, waifuID, userID, tier, agility, defense, endurance, strength, combatPower):
        waifuHaremIDquery = f"SELECT COUNT(UserID)+1 FROM HaremContract WHERE UserID={userID}"
        self.execute_query(waifuHaremIDquery)

        query = "INSERT INTO HaremContract (WaifuID, WaifuHaremID, UserID, Tier, Agility, Defense, Endurance, Strength, CombatPower) "
        query+=f"VALUES ({waifuID}, ({self.response[0][0]}), {userID}, {tier}, {agility}, {defense}, {endurance}, {strength}, {combatPower});"
        if self.execute_query(query) and len(self.response):
            return True
        else:
            return False


if __name__ == '__main__':
    db = WaifuBotDB()
    
    # Process initals from name
    for i in range(2429, 2501):
        query = f"SELECT WaifuName FROM Waifu WHERE WaifuRank={i};"
        db.execute_query(query)
        name = db.response[0][0]

        print(f"Processing {i}:", name, end="")

        result = ""
        for namepart in name.split():
            result += namepart[0] + ". "
        
        result = result[0:-2]

        print(":", result)

        query = f"UPDATE Waifu SET Initials='{result}' WHERE WaifuRank={i};"
        db.execute_query(query)