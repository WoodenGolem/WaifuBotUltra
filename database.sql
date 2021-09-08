DROP TABLE *


CREATE TABLE Waifu (
    ID           int           NOT NULL UNIQUE AUTO_INCREMENT,
    WaifuRank    int           NOT NULL UNIQUE,
    WaifuName    varchar(255)  NOT NULL,
    JapaneseName varchar(255),
    CharLink     varchar(255),
    PicLink      varchar(255),

    PRIMARY KEY (ID)
);


CREATE TABLE HaremContract (
    ID          bigint NOT NULL UNIQUE AUTO_INCREMENT,
    WaifuID     int NOT NULL,
    UserID      bigint NOT NULL,
    Tier        int NOT NULL,
    Agility     int NOT NULL,
    Defense     int NOT NULL, 
    Endurance   int NOT NULL, 
    Strength    int NOT NULL,
    CombatPower float,

    CONSTRAINT PK_HaremContract PRIMARY KEY (ID),
    FOREIGN KEY (WaifuID) REFERENCES Waifu(ID),
    FOREIGN KEY (UserID) REFERENCES User(DiscordID)
);


CREATE TABLE User (
    DiscordID     bigint       NOT NULL UNIQUE,
    UserName      varchar(255) NOT NULL,
    Discriminator int          NOT NULL,
    AvatarURL     varchar(512) NOT NULL DEFAULT "",

    WeebPoints    int          NOT NULL DEFAULT 0,
    WaifuDust     int          NOT NULL DEFAULT 0,
    Streak        int          NOT NULL DEFAULT 0,
    LastDaily     datetime     NOT NULL DEFAULT '1970-01-01 00:00:00', 

    PRIMARY KEY (DiscordID)
);


CREATE TABLE ActiveChannel (
    GuildID   bigint NOT NULL,
    ChannelID bigint NOT NULL UNIQUE,

    PRIMARY KEY (ChannelID)
);


CREATE TABLE Moderator (
    UserID  bigint NOT NULL UNIQUE,
    GuildID bigint NOT NULL,

    PRIMARY KEY (UserID),
    FOREIGN KEY (UserID) REFERENCES User(DiscordID)
);


CREATE TABLE ActiveWaifu (
    ChannelID   bigint   NOT NULL UNIQUE,
    WaifuID     int      NOT NULL,
    MessageID   bigint   NOT NULL,
    ActiveSince datetime NOT NULL,

    PRIMARY KEY (ChannelID),
    FOREIGN KEY (ChannelID) REFERENCES ActiveChannel(ChannelID),
    FOREIGN KEY (WaifuID) REFERENCES Waifu(ID)
);


CREATE TABLE TEST (
    ID int NOT NULL AUTO_INCREMENT,
    UserID int NOT NULL,

    PRIMARY KEY (ID, UserID)
);
