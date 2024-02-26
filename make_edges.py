import mysql.connector
import numpy as np

conn = mysql.connector.connect(
    host="localhost", user="eidetic", password="eideticpass", database="eidetic"
)
cursor = conn.cursor()
cursor.execute("select * from embedding")
records = cursor.fetchall()

ids = [r[0] for r in records]
embeddings = np.vstack([np.frombuffer(r[3]) for r in records])

threshold = 0.025

processed = []
average = 0
count = 0
for i in range(embeddings.shape[0]):
    for j in range(embeddings.shape[0]):
        count += 1
        dot = np.dot(embeddings[i], embeddings[j])
        average += dot
        if i != j and dot < threshold:
            print(dot)
            processed.append((records[i][2], records[j][2]))

print(average / count)

cursor.executemany(
    "insert into note_edge (note_id_a, note_id_b) values (%s, %s)", processed
)
conn.commit()

cursor.close()
conn.close()
