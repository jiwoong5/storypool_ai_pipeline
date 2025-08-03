import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='soon0729',
    db='storypool',
    charset='utf8mb4'
)

with conn.cursor() as cursor:
    sql = "SELECT scene_number, scene_image FROM pipeline_result WHERE pipeline_id = %s"
    cursor.execute(sql, ('15398690',))
    results = cursor.fetchall()

    for scene_number, image_bytes in results:
        filename = f'scene_{scene_number}.png'
        with open(filename, 'wb') as f:
            f.write(image_bytes)
        print(f"Saved: {filename}")
