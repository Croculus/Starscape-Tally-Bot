import json

with open("Ships.json") as json_file:
    ships = json.load(json_file)
def noSpace(string):
   string = string.replace('Honey Badger', 'Honey_Badger')
   string = string.replace('Hybrid Paragon', 'Hybrid_Paragon')
   string = string.replace('Hybrid Polaris', 'Hybrid_Polaris')
   string = string.replace('Hybrid Luminar', 'Hybrid_Luminar')
   string = string.replace('Hybrid Claymore', 'Hybrid_Claymore')
   return string
 # list of exception strings that need to be replaced

class kill: # main way of formatting data
    def __init__(self, victim, ship, killer, assist1, assist2):
        self.victim = victim
        self.ship = ship
        self.killer = killer
        self.assist1 = assist1
        self.assist2 = assist2

class faction:   # class to group data associated with faction
    def __init__(self, name, identifier):
        self.name = name
        self.identifier = identifier # requires list of ID factors
        self.kills = [] # holds kills attributed to faction 
        for i in self.identifier:
            ID_dict[i] = self.kills    # maps kill IDs into dictionary

    def text(self, string): #converts kills to text
        string = str('**'+self.name+' Kills:**\n')
        for i in self.kills:
            if i.assist1 == '' and i.assist2 == '':
                string += str(i.victim+' '+i.ship+' to '+i.killer+'\n') #if last kill in list, add another space for seperation 
            elif i.assist2 == '':
                string += str(i.victim+' '+i.ship+' to '+i.killer+'/'+i.assist1+'\n')
            else:
                string += str(i.victim+' '+i.ship+' to '+i.killer+'/'+i.assist1+'/'+i.assist2+'\n')
        string+= '\n'
        return string
        

       

def strtokill(string): #This function parses kill strings to be initiallized as objects
    parts = string.split(' to ')
    vict = parts[0].split()
    kfacs = parts[1].split('/')
    for i in range(len(kfacs)):
        kfacs[i]=kfacs[i].strip() 
    while(len(kfacs)) < 3:
        kfacs.append('')
    return kill(vict[0], vict[1], kfacs[0], kfacs[1], kfacs[2])


def killsort (data): #This function a list of kill objects with 1 killer into various groups
    for i in data:
        if i.assist1 == '' and i.assist2 == '': # if it's a solo kill
            ID_dict.get(i.killer, N_A.kills).append(i) #the object gets appended to the group it found in the dictionary
            continue
        assisted(i) #runs assisted kill sorter



def assisted (kill): #iterates thru kill participants, uses sets to track which lists are used
    usedLists = set() # holds used lists to deny them from being used
    killObjects = [kill.killer, kill.assist1, kill.assist2]
    for i in killObjects:
        if i == '': #empty values get skipped
            continue
        kill_Object = ID_dict.get(i, N_A.kills) #for readability


        if tuple(kill_Object) not in usedLists:
            
            kill_Object.append(kill)
            usedLists.add(tuple(kill_Object)) # list that was


def calculate(kills, dict): #put all 6 functions together
    kills2 = []
    instances = []
    export = ''
    keys = dict.keys()
    for key in keys: # turning dictionary into faction
        instance = key # faction instance variable  so group name doesn't have underscores
        if key.isidentifier() == False: # for factions like SJ-C, R-W, etc
            instance = key.replace(' ', '_') 
            instance = instance.replace('-', '_')
        exec("global "+instance+"\n"+instance+" = faction('"+key+"', "+str(dict[key])+")") #creates global variable for key, then makes faction instance of key
        instances.append(instance)
    for i in kills:
        noSpace(i)
        kills2.append(strtokill(i))

    killsort(kills2)

    for i in instances:
        string_part = eval(i+".text(export)") #instance text being printed
        export += string_part
    export += N_A.text(export)
    return(export)

def can_run(message):
    noSpace(message)
    killsort([strtokill(message)])
    N_A.kills = [] #kill gets send to N/A by default, so we reset it
    


ID_dict = {}

 # keys must be able to be value names
N_A = faction('N/A', [])
#dictionary to map identifiers to faction kill lists






