import sqlite3

def build_bolt_catalog(conn):

    sql = """
    SELECT f.nominal_size, f.length
    FROM Fastener f
    JOIN Type t ON f.type_id = t.id
    WHERE t.name NOT LIKE '%NUT%'
    AND t.name NOT LIKE '%WASHER%'
    """

    rows = conn.execute(sql).fetchall()

    bolt_catalog = {}

    for size, length in rows:
        if length is None:
            continue

        if size not in bolt_catalog:
            bolt_catalog[size] = []

        bolt_catalog[size].append(float(length))

    for size in bolt_catalog:
        bolt_catalog[size] = sorted(set(bolt_catalog[size]))

    return bolt_catalog

def select_next_length(required_length, available_lengths):

    for length in available_lengths:
        if length >= required_length:
            return length
    
    #if not found return none
    return None

FLAT_WASHER_THICKNESS = {
    "M3": 0.5,
    "M4": 0.8,
    "M5": 1.0,
    "M6": 1.6,
    "M8": 1.6,
    "M10": 2.0,
    "M12": 2.5,
    "M16": 3.0,
    "M20": 3.0,
    "M24": 4.0,
}

SPRING_WASHER_THICKNESS = {
    "M3": 0.7,
    "M4": 0.9,
    "M5": 1.2,
    "M6": 1.6,
    "M8": 2.0,
    "M10": 2.5,
    "M12": 3.0,
    "M16": 3.5,
    "M20": 4.0,
    "M24": 5.0,
}

NUT_HEIGHT = {
    "M3": 2.4,
    "M4": 3.2,
    "M5": 4.0,
    "M6": 5.0,
    "M8": 6.5,
    "M10": 8.0,
    "M12": 10.0,
    "M16": 13.0,
    "M20": 16.0,
    "M24": 19.0,
}

def required_bolt_length(sheet1, sheet2, size, joint_type):

    flat_washer = FLAT_WASHER_THICKNESS.get(size)

    if flat_washer is None:
        raise ValueError(f"Flat Washer thickness not defined for {size}")
    
    spring_washer = SPRING_WASHER_THICKNESS.get(size)

    if spring_washer is None:
        raise ValueError(f"Spring Washer thickness not defined for {size}")
    
    nut_height = NUT_HEIGHT.get(size)

    if nut_height is None:
        raise ValueError(f"Nut thickness not defined for {size}")
    
    projection = 2  # threads beyond nut

    total = sheet1 + sheet2

    if joint_type == "Through":
        total += (
            2 * flat_washer +
            spring_washer +
            nut_height +
            projection
        )
    else:  # Blind
        total += (
            flat_washer +
            spring_washer
        )

    #debug
    print("Total Length: ", total)

    return total

#Coarse Pitch Data
COARSE_PITCH = {
    "M1": 0.25,
    "M1.2": 0.25,
    "M1.4": 0.3,
    "M1.6": 0.35,
    "M1.8": 0.35,
    "M2": 0.4,
    "M2.5": 0.45,
    "M3": 0.5,
    "M3.5": 0.6,
    "M4": 0.7,
    "M5": 0.8,
    "M6": 1.0,
    "M7": 1.0,
    "M8": 1.25,
    "M10": 1.5,
    "M12": 1.75,
    "M14": 2.0,
    "M16": 2.0,
    "M18": 2.5,
    "M20": 2.5,
    "M22": 2.5,
    "M24": 3.0,
    "M27": 3.0,
    "M30": 3.5,
    "M33": 3.5,
    "M36": 4.0,
    "M39": 4.0,
    "M42": 4.5,
    "M45": 4.5,
    "M48": 5.0,
    "M52": 5.0,
    "M56": 5.5,
    "M60": 5.5,
    "M64": 6.0
}

def extract_pitch(size_str):
    try:
        if "x" in size_str:
            return float(size_str.split("x")[1])
    except Exception:
        pass
    return None

def get_bolt(conn, size, length):

    query = """
    SELECT 
        f.product_code,
        f.size,
        f.length,
        f.ft,
        t.name,
        mg.description
    FROM Fastener f
    JOIN Type t ON f.type_id = t.id
    JOIN MaterialGrade mg ON f.material_grade_id = mg.id
    WHERE t.name NOT LIKE '%NUT%'
    AND t.name NOT LIKE '%WASHER%'
    AND t.name NOT LIKE '%ALLEN%'
    AND f.nominal_size = ?
    AND f.length = ?
    """
    rows = conn.execute(query, (size, length)).fetchall()

    if not rows:
        return None

    # Get ISO coarse pitch
    coarse_pitch = COARSE_PITCH.get(size)

    if coarse_pitch is None:
        return rows[0]  # fallback

    def pitch_diff(row):
        pitch = extract_pitch(row[1]) #row[1] = f.size
        if pitch is None:
            return float("inf")  # push to end
        return abs(pitch - coarse_pitch)

    # Select closest pitch
    return min(rows, key=pitch_diff)


def get_component(conn, size, keyword):

    query = """
    SELECT 
        f.product_code,
        f.size,
        f.length,
        f.ft,
        t.name,
        mg.description
    FROM Fastener f
    JOIN Type t ON f.type_id = t.id
    JOIN MaterialGrade mg ON f.material_grade_id = mg.id
    WHERE t.name LIKE ?
    AND f.nominal_size = ?
    """

    rows = conn.execute(query, (f"%{keyword}%", size)).fetchall()

    if not rows:
        return None

    # 🔹 Only apply pitch logic for nuts
    if "NUT" in keyword.upper():
        coarse_pitch = COARSE_PITCH.get(size)

        if coarse_pitch:
            def pitch_diff(row):
                pitch = extract_pitch(row[1]) #row[1] = f.size
                if pitch is None:
                    return float("inf")
                return abs(pitch - coarse_pitch)

            return min(rows, key=pitch_diff)

    # Washers have no pitch
    for row in rows:
        if extract_pitch(row[1]) is None:
            return row

    return rows[0]

def select_fastener(conn, sheet1, sheet2, size, joint_type):

    bolt_catalog = build_bolt_catalog(conn)

    req_length = required_bolt_length(sheet1, sheet2, size, joint_type)

    if size not in bolt_catalog:
        return None

    selected_length = select_next_length(req_length, bolt_catalog[size])

    #debug
    if selected_length is not None:
        print(f"Selected Length: {selected_length}")

    if selected_length is None:
        return None

    bolt = get_bolt(conn, size, selected_length)

    #debug
    if bolt is not None:
        print(bolt)

    if bolt is None:
        print("Bolt is None")
        return None

    flat_washer = get_component(conn, size, "FLAT")

    #debug
    if flat_washer is not None:
        print(flat_washer)

    spring_washer = get_component(conn, size, "SPRING")

    if spring_washer is not None:
        print(spring_washer)

    nut = get_component(conn, size, "HEXAGON FULL NUT")

    if not all([flat_washer, spring_washer]):
        print("Washer is None")
        return None
    
    if nut is None:
        return None

    #debug
    print(f"required_length: {req_length},"
        f"selected_length: {selected_length},"
        f"bolt: {bolt},"
        f"flat_washer: {flat_washer},"
        f"spring_washer: {spring_washer},"
        f"nut: {nut}")

    return {
        "required_length": req_length,
        "selected_length": selected_length,
        "bolt": bolt,
        "flat_washer": flat_washer,
        "spring_washer": spring_washer,
        "nut": nut
    }