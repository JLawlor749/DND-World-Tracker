import re, os

def processInfo(place, type, subInfo):
    """Function to process information contained within XML location tags.\n
    place: String - The overall XML data for which you're processing the info.\n
    type: String - The type of place for which you're processing the info, e.g. 'country'.\n
    subInfo: String - The type of info you're processing, e.g. 'name'."""

    try:
        name = re.search(type + ".*?" + subInfo + "=\".*?\"", place, flags=re.DOTALL)
        name = name.group()
        name = re.sub(type + ".*?" + subInfo + "=\"", "", name, flags=re.DOTALL)
        name = re.sub("\"", "", name, flags=re.DOTALL)
    except AttributeError:
        return "N/A"
    return name



def getCountries(worldData):
    countryPattern = "<country.*?</country>"
    countries = re.findall(countryPattern, worldData, re.DOTALL)
    return countries



def countrySort(countries):
    for i in range(len(countries)):
        for j in range(len(countries)-1):
            if countries[j].name > countries[j+1].name:
                temp = countries[j]
                countries[j] = countries[j+1]
                countries[j+1] = temp
    return countries



class Shop:
    def __init__(self, locationData):
        self.name = processInfo(locationData, "shop", "name")
        self.type = processInfo(locationData, "shop", "type")
        self.locationData = locationData



class Street:
    def __init__(self, locationData):
        self.name = processInfo(locationData, "street", "name")
        self.locationData = locationData
        self.shops = []

        shopPattern = "<shop.*?</shop>"
        shops = re.findall(shopPattern, self.locationData, re.DOTALL)

        for shop in shops:
            newShop = Shop(shop)
            self.shops.append(newShop)



class Landmark:
    def __init__(self, locationData):
        self.name = processInfo(locationData, "landmark", "name")
        self.type = processInfo(locationData, "landmark", "type")
        self.location = processInfo(locationData, "landmark", "location")
        self.locationData = locationData
        


class City:
    def __init__(self, locationData):
        self.name = processInfo(locationData, "city", "name")
        self.equivalent = processInfo(locationData, "city", "equivalent")
        self.locationData = locationData
        self.streets = []
        self.landmarks = []

        streetPattern = "<street.*?</street>"
        landmarkPattern = "<landmark.*?</landmark>"
        streets = re.findall(streetPattern, self.locationData, re.DOTALL)
        landmarks = re.findall(landmarkPattern, self.locationData, re.DOTALL)

        for street in streets:
            newStreet = Street(street)
            self.streets.append(newStreet)

        for landmark in landmarks:
            newLandmark = Landmark(landmark)
            self.landmarks.append(newLandmark)

        self.allItems = self.streets + self.landmarks

    def __str__(self):
        returnString = "{} ({})".format(self.name, self.equivalent)
        returnString += "\n"

        for street in self.streets:
            returnString += "      -" + street.name + "\n"

            for shop in street.shops:
                returnString += "            ~{} (Type: {})\n".format(shop.name, shop.type)

        for landmark in self.landmarks:
            returnString += "      -{} (Type: {}, Location: {})\n".format(landmark.name, landmark.type, landmark.location)

        return returnString



class Country:
    def __init__(self, locationData):
        self.name = processInfo(locationData, "country", "name")
        self.equivalent = processInfo(locationData, "country", "equivalent")
        self.locationData = locationData
        self.cities = []

        cityPattern = "<city.*?</city>"
        cities = re.findall(cityPattern, self.locationData, re.DOTALL)

        for city in cities:
            newCity = City(city)
            self.cities.append(newCity)

    def __str__(self):
        returnString = "{} ({})".format(self.name, self.equivalent)
        returnString += "\n"
        for city in self.cities:
            returnString += "      >{} ({})\n".format(city.name, city.equivalent)

            for street in city.streets:
                returnString += "          -" + street.name + "\n"

                for shop in street.shops:
                    returnString += "                ~{} (Type: {})\n".format(shop.name, shop.type)

            for landmark in city.landmarks:
                returnString += "          -{} (Type: {}, Location: {})\n".format(landmark.name, landmark.type, landmark.location)

        return returnString
            
            

worldFilePath = "DNDWorld.xml"

worldFile = open(worldFilePath, "r", encoding="UTF-8")
worldData = worldFile.read()
worldFile.close()

countries = getCountries(worldData)
nationList = []

for country in countries:
    newCountry = Country(country)
    nationList.append(newCountry)
nationList = countrySort(nationList)

exitProgram = False

while exitProgram == False:
    print("~~~Jim's DND Geography Archive (1940s Edition)~~~")
    print("-------------------------------------------------\n")
    
    print("Detected a total [{}] countries.\n".format(len(nationList)))

    print("Please select a country by entering its number:")

    for i in range(len(nationList)):
        print("{}. {} ({})".format(i+1, nationList[i].name, nationList[i].equivalent))
    
    print("{}. {}".format(len(nationList)+1, "Print all countries info"))
    print("{}. {}".format(len(nationList)+2, "Add new country"))
    print("{}. {}".format(len(nationList)+3, "Exit"))

    selection = int(input())

    if selection == len(nationList)+1:
        print("\n")
        for nation in nationList:
            print(nation)
            print("\n")

        input("Press enter to continue")
        print("\n")
        continue

    if selection == len(nationList)+2:
        newCountryName = input("Please enter the name of your new country:\n")
        newCountryEquiv = input("Please enter the real-world equivalent of your new country (N/A if none):\n")

        newPointIndex = worldData.find("</world>")
        print(newPointIndex)

        mainData = worldData[0:newPointIndex - 1]
        newData = mainData + "\n\t<country name=\"{}\" equivalent=\"{}\">\n\n\t</country>\n\n".format(newCountryName, newCountryEquiv)
        newData = newData + "</world>"

        worldFile = open(worldFilePath, "w", encoding="UTF-8")
        worldFile.write(newData)
        worldFile.close()

        worldData = newData
        newCountries = getCountries(worldData)

        for country in newCountries:
            if country not in countries:
                newCountry = Country(country, worldData)
                nationList.append(newCountry)

        nationList = countrySort(nationList)
        continue

    if selection == len(nationList)+3:
        exitProgram = True
        break

    selectedCountry = nationList[selection-1]
    
    print("\nWhat would you like to do with {}?".format(selectedCountry.name))
    print("1. Print Info")
    print("2. Select City")
    print("3. Add City")
    print("4. Back")

    selection = int(input())

    if selection == 1:
        print("\n")
        print(selectedCountry)
        input("Press enter to continue")
        print("\n")

    if selection == 2:
        print("\nPlease select a city by entering its number:")
        cityList = selectedCountry.cities

        for i in range(len(cityList)):
            print("{}. {} ({})".format(i+1, cityList[i].name, cityList[i].equivalent))

        print("{}. {}".format(len(cityList)+1, "Exit"))

        selection = int(input())

        if selection == len(cityList)+1:
            continue

        selectedCity = cityList[selection-1]

        print("\nWhat would you like to do with {}?".format(selectedCity.name))
        print("1. Print Info")
        print("2. Select Street/Landmark")
        print("3. Back")

        selection = int(input())

        if selection == 1:
            print("\n")
            print(selectedCity)
            input("Press enter to continue")
            print("\n")

        if selection == 2:
            print("\nPlease select a street or landmark by entering its number:")
            itemList = selectedCity.allItems

            for i in range(len(itemList)):
                print("{}. {}".format(i+1, itemList[i].name))

            print("{}. {}".format(len(itemList)+1, "Exit"))
            
            selection = int(input())

            if selection == len(itemList)+1:
                continue

            selectedItem = itemList[selection-1]

            print("\nWhat would you like to do with {}?".format(selectedItem.name))
            print("1. Print Info")
            print("2. Back")

            selection = int(input())

            if selection == 1:
                print("\n")
                print(selectedItem)
                input("Press enter to continue")
                print("\n")

            if selection == 2:
                print("\n\n\n")
                continue

        if selection == 3:
            print("\n\n\n")
            continue

    if selection == 3:
        newCityName = input("Please enter the name of your new city:\n")
        newCityEquiv = input("Please enter the real-world equivalent of your new city (N/A if none):\n")

        newPointIndex = worldData.find(selectedCountry.name)

        for i in range(newPointIndex, len(worldData)):
            i = i+1
            if worldData[i] == ">":
                newPointIndex = i+1
                break

        worldDataStart = worldData[0:newPointIndex]
        worldDataFinish = worldData[newPointIndex+1:len(worldData)]

        newData = worldDataStart + "\n\n\t\t<city name=\"{}\" equivalent=\"{}\">\n\n\t\t</city>\n".format(newCityName, newCityEquiv) + worldDataFinish
        worldFile = open(worldFilePath, "w", encoding="UTF-8")
        worldFile.write(newData)
        worldFile.close()

        worldData = newData
        newCity = City("<city name=\"{}\" equivalent=\"{}\">\n\n\t\t</city>".format(newCityName, newCityEquiv), worldData)
        selectedCountry.cities.append(newCity)

        continue      

    if selection == 4:
        print("\n\n\n")
        continue