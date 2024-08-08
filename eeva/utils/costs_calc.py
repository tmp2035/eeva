translation = {ord(symb): "" for symb in ")( '"}


def parse_info(s):
    a, b, c, d, e = s.translate(translation).split(",")
    return a, int(b), int(c), int(d), int(e)


def count_miss_types(data_path, hits):
    scan_misses = 0
    get_misses = 0
    try:
        with open(data_path, "r") as f:
            _ = f.readline()  # линия с названиями столбцов

            llen = len(hits)
            for hit in hits:
                line = f.readline()
                assert len(line) != 0
                pg_id, info = line.split(";")
                pg_id, (acc_type, _, _, _, is_needed) = int(pg_id), parse_info(info)
                if hit == 0 and is_needed == 1:
                    if acc_type == "get":
                        get_misses += 1
                    elif acc_type == "scan_all":
                        scan_misses += 1
                    else:
                        raise ValueError("wtf man")
        return scan_misses / llen, get_misses / llen
    except Exception:
        return 0.5, 0.5


def calculate_cost(data_path, hits, c_scan, c_get):
    cost = 0.0
    scan_misses = 0
    get_misses = 0
    with open(data_path, "r") as f:
        _ = f.readline()  # линия с названиями столбцов
        llen = len(hits)
        for hit in hits:
            line = f.readline()
            assert len(line) != 0
            pg_id, info = line.split(";")
            pg_id, (acc_type, _, _, _, is_needed) = int(pg_id), parse_info(info)
            if hit == 0 and is_needed == 1:
                if acc_type == "get":
                    cost += c_get
                    get_misses += 1
                elif acc_type == "scan_all":
                    cost += c_scan
                    scan_misses += 1
                else:
                    raise ValueError("wtf man")
    return cost, scan_misses / llen, get_misses / llen
