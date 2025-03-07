import string
#update bottles_key and price_dict if you would like to incorporate the price functionality
bottles_key = ['Bottle 1', 'Bottle 2', 'Bottle 3']
letters = string.ascii_lowercase[:len(bottles_key)]

price_dict = {'Bottle 1':35, 'Bottle 2':25, 'Bottle 3':70}

# Combine letters with the bottles
bottles_with_keys = {letter: bottle for letter, bottle in zip(letters, bottles_key)}

# Print the result
for letter, bottle in bottles_with_keys.items():
    print(f"{letter}: {bottle}")
