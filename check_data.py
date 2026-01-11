import sqlite3
conn = sqlite3.connect('D:/github/cesiumapartment/backend/water_platform.db')
c = conn.cursor()

print('IP1相关数据时间范围:')
r = c.execute("SELECT MIN(time), MAX(time), COUNT(*) FROM measurements WHERE point_code LIKE 'IP1%'").fetchone()
print(f'最早: {r[0]}')
print(f'最晚: {r[1]}')
print(f'数量: {r[2]}')

print('\n最近30天数据:')
r2 = c.execute("SELECT COUNT(*) FROM measurements WHERE time >= datetime('now', '-30 days')").fetchone()
print(f'数量: {r2[0]}')

conn.close()
