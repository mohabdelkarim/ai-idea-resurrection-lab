import datetime
import sys

def calculate_vacation_dates(start_date, end_date):
    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        delta = end_date - start_date
        return [(start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return []

def main():
    try:
        start_date = "2024-08-06"
        end_date = "2024-08-24"
        vacation_dates = calculate_vacation_dates(start_date, end_date)
        print("Antirez's summer vacation dates are:")
        for date in vacation_dates:
            print(date)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    print("Enjoy your summer vacation!")