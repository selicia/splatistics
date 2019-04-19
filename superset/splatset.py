import os, json, sqlite3

script_dir = os.path.dirname(os.path.realpath(__file__))

with open(script_dir + "/../data/weapons.json", "r", encoding="utf-8") as weapons_json:
    weapons = json.loads(weapons_json.read())

with open(script_dir + "/../data/weapon_popularity.json", "r", encoding="utf-8") as weapon_popularity_json:
    weapon_popularity = json.loads(weapon_popularity_json.read())

conn = sqlite3.connect('splatistics.db')
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS weapons")
c.execute("CREATE TABLE weapons (" +
    "name TEXT PRIMARY KEY,"
    "class TEXT," +
    "sub TEXT," +
    "special TEXT," +
    "special_cost INTEGER," +
    "ink_saver TEXT," +
    "ink_per_shot REAL," +
    "speed_level TEXT," +
    "base_speed REAL," +
    "shooting_speed TEXT," +
    "level INTEGER," +
    "price INTEGER," +
    "min_damage REAL," +
    "max_damage REAL," +
    "mpu_max_damage REAL," +
    "sheldon_range INTEGER," +
    "sheldon_damage INTEGER," +
    "sheldon_fire_rate INTEGER," +
    "sheldon_ink_speed INTEGER," +
    "sheldon_handling INTEGER," +
    "sheldon_charge_speed INTEGER," +
    "sheldon_mobility INTEGER," +
    "sheldon_durability INTEGER," +
    "x_rank_popularity INTEGER)")

for weapon in weapons:
    values = []
    values.append(weapon["name"]) if "name" in weapon else values.append(None)
    values.append(weapon["class"]) if "class" in weapon else values.append(None)
    values.append(weapon["sub"]) if "sub" in weapon else values.append(None)
    values.append(weapon["special"]) if "special" in weapon else values.append(None)
    values.append(weapon["specialCost"]) if "specialCost" in weapon else values.append(None)
    values.append(weapon["inkSaver"]) if "inkSaver" in weapon else values.append(None)
    values.append(weapon["inkPerShot"]) if "inkPerShot" in weapon else values.append(None)
    values.append(weapon["speedLevel"]) if "speedLevel" in weapon else values.append(None)
    values.append(weapon["baseSpeed"]) if "baseSpeed" in weapon else values.append(None)
    values.append(weapon["shootingSpeed"]) if "shootingSpeed" in weapon else values.append(None)
    values.append(weapon["level"]) if "level" in weapon else values.append(None)
    values.append(weapon["price"]) if "price" in weapon else values.append(None)
    values.append(weapon["minDamage"]) if "minDamage" in weapon else values.append(None)
    values.append(weapon["maxDamage"]) if "maxDamage" in weapon else values.append(None)
    values.append(weapon["mpuMaxDamage"]) if "mpuMaxDamage" in weapon else values.append(None)
    values.append(weapon["stats"]["{{ SHELDON_RANGE | translate }}"]) if "{{ SHELDON_RANGE | translate }}" in weapon["stats"] else values.append(None)
    values.append(weapon["stats"]["{{ SHELDON_DAMAGE | translate }}"]) if "{{ SHELDON_DAMAGE | translate }}" in weapon["stats"] else values.append(None)
    values.append(weapon["stats"]["{{ SHELDON_FIRE_RATE | translate }}"]) if "{{ SHELDON_FIRE_RATE | translate }}" in weapon["stats"] else values.append(None)
    values.append(weapon["stats"]["{{ SHELDON_INK_SPEED | translate }}"]) if "{{ SHELDON_INK_SPEED | translate }}" in weapon["stats"] else values.append(None)
    values.append(weapon["stats"]["{{ SHELDON_HANDLING | translate }}"]) if "{{ SHELDON_HANDLING | translate }}" in weapon["stats"] else values.append(None)
    values.append(weapon["stats"]["{{ SHELDON_CHARGE_SPEED | translate }}"]) if "{{ SHELDON_CHARGE_SPEED | translate }}" in weapon["stats"] else values.append(None)
    values.append(weapon["stats"]["{{ SHELDON_MOBILITY | translate }}"]) if "{{ SHELDON_MOBILITY | translate }}" in weapon["stats"] else values.append(None)
    values.append(weapon["stats"]["{{ SHELDON_DURABILITY | translate }}"]) if "{{ SHELDON_DURABILITY | translate }}" in weapon["stats"] else values.append(None)

    if weapon["name"] in weapon_popularity:
        values.append(100 - weapon_popularity.index(weapon["name"]))
    else:
        values.append(0)

    c.execute("INSERT INTO weapons VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
    conn.commit()    