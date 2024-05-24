import csv

def compare_csv_values(csv_file1, csv_file2, value_to_compare):
    """
    Compares values from two CSV files and returns the values
    present in the first file but not in the second.

    Parameters:
    csv_file1 (str): Path to the first CSV file.
    csv_file2 (str): Path to the second CSV file.

    Returns:
    list: A list of values that are in csv_file1 but not in csv_file2.
    """
    def read_column_values(csv_file):
        """
        Reads values from a CSV file and returns them as a set.

        Parameters:
        csv_file (str): Path to the CSV file.

        Returns:
        set: A set of values.
        """
        column_values = set()
        with open(csv_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                column_values.add(row[value_to_compare])
        return column_values

    column_values_file1 = read_column_values(csv_file1)
    column_values_file2 = read_column_values(csv_file2)

    return list(column_values_file1 - column_values_file2)

# Example usage:
differences = compare_csv_values('dev-A.csv', 'dev-B.csv', 'MD5')
print(differences)
