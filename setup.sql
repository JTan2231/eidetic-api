create database if not exists eidetic_dev;

CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    UNIQUE KEY unique_username (username)
);

CREATE TABLE note (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id int not null,
    content TEXT NOT NULL,
    title VARCHAR(256) NOT NULL,
    hash VARCHAR(64) NOT NULL,

    constraint fk_user foreign key (user_id) references user(user_id)
);

CREATE TABLE note_edge (
    edge_id INT AUTO_INCREMENT PRIMARY KEY,
    note_id_a INT NOT NULL,
    note_id_b INT NOT NULL,
    CONSTRAINT fk_note_a FOREIGN KEY (note_id_a) REFERENCES note(note_id),
    CONSTRAINT fk_note_b FOREIGN KEY (note_id_b) REFERENCES note(note_id),
    CONSTRAINT chk_different_nodes CHECK (note_id_a != note_id_b),
    UNIQUE KEY unique_edge (note_id_a, note_id_b)
);
