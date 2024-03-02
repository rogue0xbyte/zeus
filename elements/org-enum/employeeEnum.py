from crosslinked import CrossLinked

def get_employees(company_name):
    try:
        employees = CrossLinked('google', company_name, timeout=15).search()
        if employees:
            return employees
        else:
            employees = CrossLinked('bing', company_name, timeout=15).search()
            if employees:
                return employees
            else:
                return []
    except:
        employees = CrossLinked('bing', company_name, timeout=15).search()
        if employees:
            return employees
        else:
            return []

if __name__ == "__main__":
    company_name = "PSG College of Technology"
    print(get_employees(company_name))