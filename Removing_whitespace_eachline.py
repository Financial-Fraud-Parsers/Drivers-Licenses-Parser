import os

directory = "/Users/iamns45/Desktop/Drivers_Licenses_Parser-main/copy"

for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        with open(os.path.join(directory, filename), "r") as file:
            # Read the contents of the file and remove leading whitespace from each line
            contents = [line.lstrip() for line in file.readlines()]

        # Write the modified contents back to the file
        with open(os.path.join(directory, filename), "w") as file:
            file.write("\n".join(contents))
