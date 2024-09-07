import csv
import sys

def parse_invoice_to_csv(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # Extract relevant data
    items = []
    description, quantity, amount = None, None, None
    for line in lines:
        if "Description:" in line:
            description = line.split("Description:")[1].split("has confidence:")[0].strip()
        if "Quantity:" in line:
            quantity = line.split("Quantity:")[1].split("has confidence:")[0].strip()
        if "Amount:" in line:
            amount = line.split("Amount:")[1].split("has confidence:")[0].strip()
            items.append([description if description else "item1", 
                          quantity if quantity else "1", 
                          amount if amount else "null000"])
            description, quantity, amount = None, None, None  # Reset for the next item

    # Write to a CSV file
    with open(output_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Description', 'Quantity', 'Amount']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in items:
            writer.writerow({'Description': item[0], 'Quantity': item[1], 'Amount': item[2]})

def main(input_file_path, output_file_path):
    parse_invoice_to_csv(input_file_path, output_file_path)
    print(f"CSV file has been created at: {output_file_path}")

if __name__ == "__main__":
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    main(input_filename, output_filename)
