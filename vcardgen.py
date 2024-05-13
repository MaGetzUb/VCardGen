
import sqlite3
import io
import os
import sys
import datetime
import time


# There's probably libraries for exporting vcards
# but the format seemed simple enough
# https://en.wikipedia.org/wiki/VCard
def WriteVCard(file, entry):

	file.write("BEGIN:VCARD\n")

	line = "N:"
	if entry['lastName'] is not None:
		line += f"{entry['lastName']}"
	line += ";"


	if entry['firstName'] is not None:
		line += f"{entry['firstName']}"
	line += ";"

	file.write(f"{line};\n")
	file.write(f"TEL;TYPE=cell:{entry['phoneNumber']}\n")
	if entry["email"] is not None:
		file.write(f"EMAIL;TYPE=personal:{entry['email']}\n")

	if entry["birthday"] is not None:
		file.write(f"BDAY:{entry['bday']}\n")

	file.write("END:VCARD\n")

# This vcard generator is very simplistic it generates
# First+Last Name, Phone Number, and optionally Email and Birthday.
if __name__ == "__main__":

	if len(sys.argv) < 2:
		print("Not database file provided! Usage: vcardgen <path/to/database.db>")

	con = sqlite3.connect(sys.argv[1])
	cur = con.cursor()

	contacts = {}

	# Fetch first and last name...
	cur.execute("SELECT contactId,firstName,lastName FROM Names;")
	for contact in cur.fetchall():
		contacts[contact[0]] = {
		    "firstName":contact[1],
			"lastName":contact[2],
			"phoneNumber":None,
			"email":None,
			"birthday":None
		}

	# ...phonenumber...
	cur.execute("SELECT contactId,phoneNumber FROM PhoneNumbers;")
	for contact in cur.fetchall():
		if contact[0] in contacts:
			contacts[contact[0]]["phoneNumber"] = contact[1]

	# ...email...
	cur.execute("SELECT contactId,emailAddress FROM EmailAddresses;")
	for contact in cur.fetchall():
		if contact[0] in contacts:
			contacts[contact[0]]["email"] = contact[1]

	# ...and birthdays.
	cur.execute("SELECT contactId,birthday FROM Birthdays;")
	for contact in cur.fetchall():
		if contact[0] in contacts:
			splits = contact[1].split('-')
			contacts[contact[0]]["bday"] = "".join(splits)

	# Create output folder under current working directory
	if not os.path.exists("vcards"):
		os.mkdir("vcards")


	found = set()
	result = {}

	# Filter out duplicate contacts, or contacts that has no phone number attached to it.
	for contact in contacts:

		# Build combined string for the final file name and key.
		firstLast = str()

		# Add first name if it exists
		if contacts[contact]['firstName'] is not None:
			firstLast += contacts[contact]['firstName']

		# Add last name if it exists
		if contacts[contact]['lastName'] is not None:
			firstLast += " "
			firstLast += contacts[contact]['lastName']

		# Skip "null" contact
		if len(firstLast) == 0:
			continue

		# Generate key for dictionary lookup
		firstLastLower = firstLast.lower()

		# If contact has phone number, and the key doesn't exist in the dictionary
		if contacts[contact]["phoneNumber"] is not None and not firstLastLower in found:
			result[firstLast]=contacts[contact]
			found.add(firstLastLower)

	# Navigate into output directory and spit out the results
	os.chdir("vcards")
	for res in result:
		with io.open(f"{res}.vcard", "w") as file:
			WriteVCard(file, result[res])

	# Navigate back and we're done
	os.chdir("..")




