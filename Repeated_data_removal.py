import os

directory = "/Users/iamns45/Desktop/Drivers_Licenses_Parser-main/copy"

for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        with open(os.path.join(directory, filename), "r") as file:
            # Read the first line of the file
            first_line = file.readline().rstrip()

            # Read the rest of the file and replace the text with space
            data = file.read()
            second_index = data.find(first_line, len(first_line))
            if second_index != -1:
                new_data = data[:second_index] + " " * (len(data) - second_index)
                with open(os.path.join(directory, filename), "w") as output_file:
                    output_file.write(first_line + "\n" + new_data)



