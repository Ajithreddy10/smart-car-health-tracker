
import json
from pathlib import Path
from datetime import date

DATA_FILE = Path(__file__).with_name("car_data.json")


# -------------------- DATA MANAGEMENT --------------------

def load_data():
    empty_data = {"car": None, "services": [], "bills": []}

    if not DATA_FILE.exists():
        return empty_data.copy()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Invalid data format.")

        data.setdefault("car", None)
        data.setdefault("services", [])
        data.setdefault("bills", [])
        return data

    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Could not load saved data: {error}")
        print("Starting with empty data. Your existing file is unchanged.")
        return empty_data.copy()


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return True
    except OSError as error:
        print(f"Error saving data: {error}")
        return False


def ask_text(message, default=None):
    while True:
        value = input(message).strip()

        if value:
            return value

        if default is not None:
            return default

        print("This field cannot be empty.")


def ask_number(message, minimum=0):
    while True:
        try:
            value = float(input(message).strip())

            if value < minimum:
                print(f"Enter a number greater than or equal to {minimum}.")
                continue

            return value

        except ValueError:
            print("Enter a valid number.")


def ask_integer(message, minimum=1):
    while True:
        try:
            value = int(input(message).strip())

            if value < minimum:
                print(f"Enter a whole number of at least {minimum}.")
                continue

            return value

        except ValueError:
            print("Enter a valid whole number.")


def next_invoice_number(data):
    numbers = [
        int(bill.get("invoice_number", 0))
        for bill in data.get("bills", [])
    ]
    return max(numbers, default=0) + 1


# -------------------- CAR PROFILE --------------------

def add_car(data):
    print("\n--- ADD / UPDATE CAR PROFILE ---")

    old_car = data.get("car") or {}

    model = ask_text(
        "Car make and model: ",
        old_car.get("make_model")
    )

    registration = ask_text(
        "Registration number: ",
        old_car.get("registration", "Not entered")
    )

    year = ask_text(
        "Manufacturing year: ",
        str(old_car.get("year", "Not entered"))
    )

    current_km = ask_number(
        "Current odometer reading (km): "
    )

    interval = ask_integer(
        "Oil service interval in km (check owner's manual): "
    )

    data["car"] = {
        "make_model": model,
        "registration": registration,
        "year": year,
        "current_km": current_km,
        "oil_interval_km": interval
    }

    if save_data(data):
        print("Car profile saved successfully!")


def view_car_profile(data):
    print("\n--- CAR PROFILE ---")

    car = data.get("car")

    if not car:
        print("No car profile found.")
        print("Choose option 1 to add your car details.")
        return

    print("-" * 40)
    print(f"Car model        : {car.get('make_model', 'Not entered')}")
    print(f"Registration     : {car.get('registration', 'Not entered')}")
    print(f"Manufactured     : {car.get('year', 'Not entered')}")
    print(f"Current reading  : {float(car.get('current_km', 0)):,.0f} km")
    print(
        f"Oil service interval: "
        f"{int(car.get('oil_interval_km', 10000)):,} km"
    )

    last_oil_km = None

    for service in reversed(data.get("services", [])):
        service_type = service.get("service_type", "").strip().lower()

        if service_type in ("oil change", "engine oil change"):
            last_oil_km = float(service.get("odometer_km", 0))
            break

    if last_oil_km is None:
        print("Oil service status: No oil-change record")
    else:
        interval = int(car.get("oil_interval_km", 10000))
        next_due = last_oil_km + interval
        current_km = float(car.get("current_km", 0))

        print(f"Last oil change  : {last_oil_km:,.0f} km")
        print(f"Next oil service : {next_due:,.0f} km")

        if current_km >= next_due:
            print("Status           : SERVICE DUE")
        else:
            print(f"Status           : {next_due - current_km:,.0f} km remaining")

    print("-" * 40)


def update_odometer(data):
    car = data.get("car")

    if not car:
        print("Please add a car profile using option 1.")
        return

    old_reading = float(car.get("current_km", 0))

    while True:
        new_reading = ask_number("Enter current odometer reading (km): ")

        if new_reading < old_reading:
            print(f"Reading cannot be lower than {old_reading:,.0f} km.")
        else:
            break

    car["current_km"] = new_reading

    if save_data(data):
        print("Odometer updated successfully!")


# -------------------- SERVICE MANAGEMENT --------------------

def record_service(data):
    if not data.get("car"):
        print("Please add a car profile using option 1.")
        return

    print("\n--- RECORD SERVICE ---")

    service_type = ask_text(
        "Service type (Oil change, Tyre replacement, etc.): "
    )
    odometer = ask_number("Odometer reading at service (km): ")
    cost = ask_number("Service cost (Rs.): ")
    service_date = ask_text(
        f"Service date [{date.today().isoformat()}]: ",
        date.today().isoformat()
    )

    service = {
        "service_type": service_type,
        "odometer_km": odometer,
        "cost_rupees": cost,
        "date": service_date
    }

    data.setdefault("services", []).append(service)

    if save_data(data):
        print("Service record saved successfully!")


def view_service_history(data):
    print("\n--- SERVICE HISTORY ---")

    services = data.get("services", [])

    if not services:
        print("No service records found.")
        return

    for index, service in enumerate(services, start=1):
        print(f"\nService {index}")
        print(f"Type     : {service.get('service_type', 'Unknown')}")
        print(f"Date     : {service.get('date', 'Unknown')}")
        print(
            f"Odometer : "
            f"{float(service.get('odometer_km', 0)):,.0f} km"
        )
        print(
            f"Cost     : "
            f"Rs. {float(service.get('cost_rupees', 0)):,.2f}"
        )


def total_service_spending(data):
    services = data.get("services", [])
    total = sum(
        float(service.get("cost_rupees", 0))
        for service in services
    )

    print("\n--- SERVICE SPENDING ---")
    print(f"Service records: {len(services)}")
    print(f"Total spending : Rs. {total:,.2f}")


# -------------------- BILLING SYSTEM --------------------

def create_bill(data):
    print("\n--- CREATE CUSTOMER BILL ---")

    customer = ask_text("Customer name: ")
    phone = ask_text("Customer phone number: ")
    car_model = ask_text("Car model: ")
    registration = ask_text("Car registration number: ")

    items = []

    while True:
        print("\n--- BILL ITEM ---")

        name = ask_text("Service or spare-part name: ")
        quantity = ask_integer("Quantity: ")
        price = ask_number("Price per item (Rs.): ")

        items.append({
            "name": name,
            "quantity": quantity,
            "price": price,
            "amount": quantity * price
        })

        print(f"Item total: Rs. {quantity * price:.2f}")

        more = input("Add another item? (y/n): ").strip().lower()

        if more != "y":
            break

    subtotal = sum(item["amount"] for item in items)

    while True:
        discount = ask_number("Discount amount (Rs.): ")

        if discount <= subtotal:
            break

        print("Discount cannot exceed the subtotal.")

    taxable_amount = subtotal - discount
    gst_rate = ask_number("GST rate (%) (enter 0 if not applicable): ")
    gst = taxable_amount * gst_rate / 100
    total = taxable_amount + gst

    bill = {
        "invoice_number": next_invoice_number(data),
        "date": date.today().isoformat(),
        "customer": customer,
        "phone": phone,
        "car_model": car_model,
        "registration": registration,
        "items": items,
        "subtotal": subtotal,
        "discount": discount,
        "gst_rate": gst_rate,
        "gst": gst,
        "total": total
    }

    data.setdefault("bills", []).append(bill)

    if save_data(data):
        print_invoice(bill)
    else:
        data["bills"].pop()


def print_invoice(bill):
    print("\n" + "=" * 54)
    print("                 CAR SERVICE INVOICE")
    print("=" * 54)

    print(f"Invoice number : INV-{int(bill['invoice_number']):04d}")
    print(f"Date           : {bill['date']}")
    print(f"Customer       : {bill['customer']}")
    print(f"Phone          : {bill['phone']}")
    print(f"Car model      : {bill['car_model']}")
    print(f"Registration   : {bill['registration']}")

    print("-" * 54)
    print(f"{'Item':22} {'Qty':>4} {'Price':>10} {'Total':>12}")
    print("-" * 54)

    for item in bill["items"]:
        name = item["name"][:22]
        print(
            f"{name:22} "
            f"{int(item['quantity']):>4} "
            f"{float(item['price']):>10.2f} "
            f"{float(item['amount']):>12.2f}"
        )

    print("-" * 54)
    print(f"{'Subtotal':>40}: Rs. {bill['subtotal']:.2f}")
    print(f"{'Discount':>40}: Rs. {bill['discount']:.2f}")
    print(
        f"{'GST (' + str(bill['gst_rate']) + '%)':>40}: "
        f"Rs. {bill['gst']:.2f}"
    )
    print(f"{'GRAND TOTAL':>40}: Rs. {bill['total']:.2f}")
    print("=" * 54)
    print("Thank you for your business!")
    print("=" * 54)


def view_bills(data):
    print("\n--- BILLING HISTORY ---")

    bills = data.get("bills", [])

    if not bills:
        print("No bills found. Choose option 7 to create a bill.")
        return

    for bill in bills:
        print(
            f"INV-{int(bill['invoice_number']):04d} | "
            f"{bill['date']} | {bill['customer']} | "
            f"Rs. {float(bill['total']):.2f}"
        )

    choice = input(
        "\nEnter invoice number to view details, or 0 to return: "
    ).strip()

    if not choice.isdigit() or int(choice) == 0:
        return

    for bill in bills:
        if int(bill["invoice_number"]) == int(choice):
            print_invoice(bill)
            return

    print("Invoice not found.")


def billing_revenue(data):
    bills = data.get("bills", [])

    revenue = sum(
        float(bill.get("total", 0))
        for bill in bills
    )

    print("\n--- BILLING SUMMARY ---")
    print(f"Total invoices : {len(bills)}")
    print(f"Total billed   : Rs. {revenue:,.2f}")


# -------------------- MENU --------------------

def show_menu():
    print("\n" + "=" * 42)
    print("       SMART CAR HEALTH TRACKER")
    print("              VERSION 1")
    print("=" * 42)
    print("1. Add / Update Car Profile")
    print("2. View Car Profile")
    print("3. Update Odometer Reading")
    print("4. Record a Service")
    print("5. View Service History")
    print("6. View Total Service Spending")
    print("7. Create Customer Bill")
    print("8. View Billing History")
    print("9. View Billing Revenue")
    print("0. Exit")
    print("=" * 42)


def main():
    data = load_data()

    actions = {
        "1": add_car,
        "2": view_car_profile,
        "3": update_odometer,
        "4": record_service,
        "5": view_service_history,
        "6": total_service_spending,
        "7": create_bill,
        "8": view_bills,
        "9": billing_revenue
    }

    while True:
        show_menu()
        choice = input("Choose an option (0-9): ").strip()

        if choice == "0":
            print("Thank you for using Smart Car Health Tracker!")
            break

        action = actions.get(choice)

        if action is None:
            print("Invalid choice. Enter a number from 0 to 9.")
            continue

        try:
            action(data)
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
        except (TypeError, ValueError, KeyError) as error:
            print(f"Operation failed: {error}")

        try:
            input("\nPress Enter to return to the menu...")
        except (KeyboardInterrupt, EOFError):
            print()


if __name__ == "__main__":
    main()
