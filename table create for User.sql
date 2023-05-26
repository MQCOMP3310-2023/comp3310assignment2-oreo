-- CREATE TABLE Users (
--     UserID INT NOT NULL,
--     Username VARCHAR(64) NOT NULL,
--     PasswordHash VARCHAR(128) NOT NULL,
--     FirstName VARCHAR(250) NOT NULL,
--     LastName VARCHAR(250) NOT NULL,
--     Role VARCHAR(20) NOT NULL CHECK (Role IN ('Guest', 'Owner', 'Admin')),
--     DOB DATETIME NOT NULL,
--     PRIMARY KEY (UserID)
-- );


CREATE TABLE Rating (
    id INTEGER PRIMARY KEY,
    value INTEGER NOT NULL,
    restaurant_id INTEGER NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (restaurant_id) REFERENCES restaurant (id),
    FOREIGN KEY (user_id) REFERENCES Users (UserID)
);
