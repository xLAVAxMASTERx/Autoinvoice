import pandas as pd
import matplotlib.pyplot as plt
import sys
import re

def main(input_filename, output_filename):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_filename)

    # Remove non-numeric characters (such as currency symbols) from the 'Amount' column
    df['Amount'] = df['Amount'].apply(lambda x: re.sub(r'[^\d.]', '', str(x)))
    
    # Ensure the 'Amount' column is numeric, converting non-numeric values to NaN
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df['Amount'].fillna(0, inplace=True)  # Replace NaN values with 0

    # Create a figure and two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 16))

    # Create the first bar plot for quantity
    ax1.bar(df['Description'], df['Quantity'], color='skyblue')
    ax1.set_title('Quantity per Product')
    ax1.set_xlabel('Product Name')
    ax1.set_ylabel('Quantity')
    ax1.tick_params(axis='x', rotation=45)

    # Create the second bar plot for amount
    ax2.bar(df['Description'], df['Amount'], color='lightgreen', bottom=0)
    ax2.set_title('Total Amount per Product')
    ax2.set_xlabel('Product Name')
    ax2.set_ylabel('Amount')
    ax2.set_ylim(0, df['Amount'].max() * 1.1)  # Adding some space above the maximum value
    ax2.tick_params(axis='x', rotation=45)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Save the image
    plt.savefig(output_filename)

    # Show the plot (optional)

if __name__ == "__main__":
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    main(input_filename, output_filename)

