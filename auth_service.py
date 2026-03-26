def verify_staff(role, staff_code):
    if role == "staff":
        return staff_code == "STAFF2026"
    return True