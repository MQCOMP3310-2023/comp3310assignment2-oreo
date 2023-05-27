CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY,
    email VARCHAR(250) NOT NULL,
    Username VARCHAR(64) NOT NULL,
    PasswordHash VARCHAR(128) NOT NULL,
    FirstName VARCHAR(250) NOT NULL,
    LastName VARCHAR(250) NOT NULL,
    Role INT NOT NULL,
    DOB DATETIME NOT NULL
    
);


CREATE TABLE Rating (
    id INTEGER PRIMARY KEY,
    value INTEGER NOT NULL,
    restaurant_id INTEGER NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (restaurant_id) REFERENCES restaurant (id),
    FOREIGN KEY (user_id) REFERENCES Users (UserID)
);
