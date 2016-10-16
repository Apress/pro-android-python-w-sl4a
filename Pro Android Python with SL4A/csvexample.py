import itertools
import csv

HeaderFields = ["Name", "City", "State", "Zip", "PhoneNum"]

infile = open("testdata.txt")

contacts = csv.DictReader(infile, HeaderFields, delimiter="|")

for header in itertools.izip(contacts):
    print "Header (%d fields): %s" % (len(header), header)
