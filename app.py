import sqlite3

#Database connection
conn = sqlite3.connect("fasteners.db")

cur = conn.cursor()

if conn:
    print("Database connected successfully!")
else:
    print("Database connection failed!")

#test query
sql = """
        SELECT f.nominal_size, f.length
        FROM Fastener f
        JOIN Type t ON f.type_id = t.id
        WHERE t.name NOT LIKE '%NUT%'
        AND t.name NOT LIKE '%WASHER%'
    """

rows = cur.execute(sql).fetchall()

# print("Check:\n")
# for r in rows:
#     print(r)

#Bolt Catalog Dictionary
bolt_catalog = {}

for size,length in rows:

    if length is None:
        continue

    if size not in bolt_catalog:
        bolt_catalog[size] = []
    
    bolt_catalog[size].append(length)

#loop and remove the duplicates as well as sort it
for size in bolt_catalog:
    # bolt_catalog[size] = sorted(set(bolt_catalog[size])) #float form if needed
    bolt_catalog[size] = sorted(set(int(l) for l in bolt_catalog[size])) #if needed in integer form

# print("\nBolt Catalog:\n")
# print(bolt_catalog)

def select_next_length(required_length, available_lengths):

    for length in available_lengths:
        if length >= required_length:
            return length
    
    #if not found return none
    return None

def required_bolt_length(sheet1, sheet2):

    flat_washer = 1.6
    spring_washer = 2.5
    nut_height = 5
    projection = 2

    total = (
        sheet1 +
        sheet2 +
        2 * flat_washer +
        spring_washer +
        nut_height +
        projection
    )

    return total

def get_bolt(conn, size, length):

    query = """
    SELECT f.product_code, f.nominal_size, f.length
    FROM Fastener f
    JOIN Type t ON f.type_id = t.id
    WHERE t.name NOT LIKE '%NUT%'
    AND t.name NOT LIKE '%WASHER%'
    AND f.nominal_size = ?
    AND f.length = ?
    LIMIT 1
    """

    return conn.execute(query, (size, length)).fetchone()

def get_component(conn, size, keyword):

    query = """
            SELECT f.product_code, t.name, f.nominal_size
            FROM Fastener f
            JOIN Type t on f.type_id = t.id
            WHERE t.name LIKE ?
            AND f.nominal_size = ?
            LIMIT 1
            """
    
    return conn.execute(query, (f"%{keyword}%", size)).fetchone()

def select_fastener(conn, sheet1, sheet2, size):
    req_length = required_bolt_length(sheet1,  sheet2)
    selected_length = select_next_length(req_length, bolt_catalog[size])
    bolt = get_bolt(conn, size, selected_length)

    flat_washer = get_component(conn, size, "FLAT")
    spring_washer = get_component(conn, size, "SPRING")
    nut = get_component(conn, size, "HEXAGON FULL NUT")

    return {
        "required_length": req_length,
        "selected_length": selected_length,
        "bolt": bolt,
        "flat_washer": flat_washer,
        "spring_washer": spring_washer,
        "nut": nut
    }

conn.close()
