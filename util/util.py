import ast


def csv_to_list(csv):
    list = []
    try:
        list = csv.split(",")
        for i in range(0, len(list)):
            list[i] = list[i].strip()
    except Exception as e:
        print(e)
        pass
    return list


def list_to_csv(list):
    csv = ""
    try:
        csv = list[0]
        for item in range(1, len(list)):
            csv += ", " + list[item]
    except Exception as e:
        print(e)
        pass
    return csv


def string_to_object(s):
    try:
        return ast.literal_eval(s)
    except Exception as e:
        print(e)
        return None


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
