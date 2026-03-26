def enter_area(cur, area):
    cur.execute("UPDATE areas SET count=count+1 WHERE area_code=?", (area,))

def exit_area(cur, area):
    cur.execute("UPDATE areas SET count=count-1 WHERE area_code=? AND count>0", (area,))