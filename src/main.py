"""
Postal Service Routing Program Implementation
By Jonathan Lane
Student ID: 001264312
"""

from postal_hash_table import PostalHashTable

testTable = PostalHashTable(2)
print(testTable.get_buckets())

testTable.insert("help")
testTable.insert("I'm stuck!")
testTable.insert("wowow")
testTable.insert(2)
testTable.insert(3)


print(testTable.get_buckets())

print(testTable.lookup("help"))
print(testTable.lookup("I'm stuck!"))
print(testTable.lookup("wowow"))
print(testTable.lookup(2))
print(testTable.lookup(3))
print(testTable.lookup("not here"))
