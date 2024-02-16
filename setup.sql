create database if not exists yangnet;

CREATE TABLE paper (
    paper_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    abstract TEXT,
    publication_date DATE
);

CREATE TABLE author (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    affiliation VARCHAR(255)
);

CREATE TABLE citation (
    citing_paper_id INT,
    cited_paper_id INT,
    PRIMARY KEY (citing_paper_id, cited_paper_id),
    FOREIGN KEY (citing_paper_id) REFERENCES paper(paper_id),
    FOREIGN KEY (cited_paper_id) REFERENCES paper(paper_id)
);

CREATE TABLE paper_author (
    paper_id INT,
    author_id INT,
    PRIMARY KEY (paper_id, author_id),
    FOREIGN KEY (paper_id) REFERENCES paper(paper_id),
    FOREIGN KEY (author_id) REFERENCES author(author_id)
);
