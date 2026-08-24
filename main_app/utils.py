def check_field_values(fields):
    truthy = []
    for field in fields:
        if not field or len(field) < 1:
            truthy.append(False)
    return truthy