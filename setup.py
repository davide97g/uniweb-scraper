# setup.py
from os import path

dotenv_file = "./app/.env"

if path.isfile(dotenv_file):
    print(".env file already present: checking variables...")
    f = open(dotenv_file, "r")
    variables_required = ["MONGODB_CONNECTION_STRING",
                          "UNIWEB_USERNAME",
                          "UNIWEB_PASSWORD"]
    variables_read = {}
    for row in f.read().split("\n"):
        [name, value] = row.split(" = ")
        variables_read[name.replace(" ", "")] = value

    for variable in variables_required:
        if variable not in variables_read:
            print(f"{variable} not present. Need to set it")
            variable_value = input(f"{variable} : ")
            variables_read[variable] = variable_value

    for variable in variables_read.keys():
        print(variable, variables_read.get(variable))
else:
    print(".env file missing: creating one...\n")
    mongodb_connection_string = input(
        "DB Connection String \nIf you don't know your connection string, please check here how to get it:\nhttps://docs.atlas.mongodb.com/tutorial/connect-to-your-cluster/\nMongoDB Connection String : ")
    uniweb_username = input("Uniweb username: ")
    uniweb_password = input("Uniweb password: ")
    variables = [["MONGODB_CONNECTION_STRING", mongodb_connection_string],
                 ["UNIWEB_USERNAME", uniweb_username],
                 ["UNIWEB_PASSWORD", uniweb_password]]
    f = open(dotenv_file, "w")
    for variable in variables:
        f.write(variable[0] + " = " + "\"" + variable[1] + "\"\n")
    f.close()
    print(f"{dotenv_file} created")
