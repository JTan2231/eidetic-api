create database if not exists eidetic;

CREATE TABLE if not exists user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    UNIQUE KEY unique_username (username)
);

CREATE TABLE if not exists note (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id int not null,
    content TEXT NOT NULL,
    title VARCHAR(256) NOT NULL,
    hash VARCHAR(64) NOT NULL,

    constraint fk_user foreign key (user_id) references user(user_id)
);

CREATE TABLE if not exists note_edge (
    edge_id INT AUTO_INCREMENT PRIMARY KEY,
    note_id_a INT NOT NULL,
    note_id_b INT NOT NULL,
    CONSTRAINT fk_note_a FOREIGN KEY (note_id_a) REFERENCES note(note_id),
    CONSTRAINT fk_note_b FOREIGN KEY (note_id_b) REFERENCES note(note_id),
    CONSTRAINT chk_different_nodes CHECK (note_id_a != note_id_b),
    UNIQUE KEY unique_edge (note_id_a, note_id_b)
);

create table if not exists embedding (
    embedding_id int auto_increment primary key,
    user_id int not null,
    note_id int not null,
    data blob not null,
    tsne_x decimal(10, 6) not null,
    tsne_y decimal(10, 6) not null,

    constraint fk_user_embedding foreign key (user_id) references user(user_id),
    constraint fk_note_embedding foreign key (note_id) references note(note_id)
);
