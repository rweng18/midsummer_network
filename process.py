###############################################################################
##     IMPORT PACKAGES     ####################################################
###############################################################################

import re

###############################################################################
##     HELPER FUNCTIONS     ###################################################
###############################################################################

def get_empty_appearances(characters, num = False):

    '''Create dictionary of dictionaries to track coappearances of characters

    Parameters
    ----------
    characters: list of character names

    num       : whether or not the dictionary of dictionaries should initialize
                to 0 (True) or an empty list (False)

    Returns
    -------
    Dictionary of dictionaries where each key is each character and each value
    is a dictionary with all other characters as keys, and values as 0 or [].
    '''

    appearances = {}
    for character in characters:
        companions = {}
        for companion in characters:
            if companion != character:

                if num:
                    companions[companion] = 0

                else:
                    companions[companion] = []
        appearances[character] = companions
    return appearances


def switch_char(old_char, new_char, lst):

    '''Switch character name in list

    Parameters
    ----------
    old_char: character name to be replaced

    new_char: character name to replace with

    lst     : list of character names

    Returns
    -------
    A list of character names with the old_char replaced with the new_char
    '''

    new_lst = [char for char in lst]
    new_lst.remove(old_char)

    # Check for existing duplicate
    if new_char not in new_lst:
        new_lst.extend([new_char])
    return new_lst

###############################################################################
##     ADD COAPPEARANCE FUNCTION     ##########################################
###############################################################################

def add_coappear(curr_lst, entered_lst, appearances, scene, internal_cast):

    '''Add coappearances between those who entered and those who are in the scene

    Parameters
    ----------
    curr_lst     : characters currently in the scene

    entered_lst  : characters that just entered

    appearances  : dictionary of dictionaries to store appearances

    scene        : scene number

    internal_cast: dictionary connecting cast to cast in play within a play

    Returns
    -------
    An updated dictionary of dictionaries with added coappearances
    '''

    # Create new lists for char_names (entered) and current_chars
    # Fairy = Fairies
    # Lords/Attendants = Attendants
    current_chars = [char for char in curr_lst]
    char_names    = [char for char in entered_lst]

    char_dict     = {'Fairy': 'Fairies',
                     'Lords': 'Attendants'}

    # Adjust names in current_chars and char_names (entered) for Fairies/Lords
    for char_key in char_dict.keys():
        if char_key in current_chars:
            current_chars = switch_char(char_key, char_dict[char_key],
                                        current_chars)
        if char_key in char_names:
            char_names    = switch_char(char_key, char_dict[char_key],
                                        char_names)

    # Adjust names in current_chars and char_names (entered) for internal cast
    for char_key in internal_cast.keys():
        if char_key in current_chars:
            current_chars = switch_char(char_key, internal_cast[char_key],
                                        current_chars)
        if char_key in char_names:
            char_names    = switch_char(char_key, internal_cast[char_key],
                                        char_names)

    # Handle Train, which can be Attendants or Fairies
    if 'Train' in char_names:
        if ('Oberon' in char_names) | ('Titania' in char_names):
            char_names = switch_char('Train', 'Fairies', char_names)

        elif ('Egeus' in char_names):
            char_names = switch_char('Train', 'Attendants', char_names)

    # Add co-appearances with each other
    for char in char_names:
        if char in appearances.keys():
            for co_char in char_names:
                if (co_char != char) & (co_char in appearances.keys()):
                    if scene not in appearances[char][co_char]:
                        appearances[char][co_char].extend([scene])

    # Add co-appearances with characters already in scene
    if len(current_chars) != 0:
        for char in current_chars:
            if char in appearances.keys():
                for co_char in char_names:
                    if (co_char != char) & (co_char in appearances.keys()):

                        # Check for duplicates
                        if scene not in appearances[char][co_char]:
                            appearances[char][co_char].extend([scene])

                        if scene not in appearances[co_char][char]:
                            appearances[co_char][char].extend([scene])

    return appearances

###############################################################################
##     MAIN FUNCTION     ######################################################
###############################################################################

def get_coappear(scene, act, int_cast_dict, all_appearances):

    '''Get coappearances that occur throughout a given scene's text

    Parameters
    ----------
    scene          : scene text, starts with scene number (I., II., III., ...)

    act            : string for act number in Roman numerals (I, II, III, ...)

    int_cast_dict  : dictionary for cast of play within a play

    all_appearances: dictionary of dictionaries for coappearances between all
                     characters in the play

    Returns
    -------
    An updated dictionary of dictionaries with added coappearances
    '''

    # Get stage directions before characters enter
    intro = scene.split('Enter')[0].strip()

    # Find all entrances, exits, and sleeping
    all_results = re.findall('(Enter [A-Za-z,:; \n’]+\.|[A-Z]+\.|Exit [A-Za-z, \n]+\.|Exit.|Exeunt [A-Za-z, \n]+\.|Exeunt.|\[_.*[Ss]leep.*_])', scene)
    all_results = [result.strip('[_').strip('_]') for result in all_results]

    curr_char = []  # Characters currently in scene
    prev_speak = '' # Who is current speaker likely speaking to
    curr_speak = '' # Who is the current speaker, can track who is exiting
    asleep = []     # Characters currently asleep (cannot exeunt)

    for result in all_results:

        print(result)

        # CASE: Get the act + scene number
        if result in ['I.', 'II.']:
            if curr_char == []:
                scene = act + result.strip('.').lower()

                # CASE: sleeping characters being in scene already
                # Get character names, add to current character
                # and sleeping lists
                if 'asleep' in intro:

                    # SPECIAL CASE: Titania referred to as The Queen
                    if 'The Queen' in intro:
                        asleep.extend(['Titania'])
                        curr_char.extend(asleep)

                    # CASE: all other sleeping characters
                    else:
                        chars = re.findall('[A-Z][a-z]+', intro.split('\n')[-1].strip())
                        asleep.extend(chars)
                        all_appearances = add_coappear(curr_char, asleep,
                                                       all_appearances, scene,
                                                       int_cast_dict)
                        curr_char.extend(asleep)

            else:
                continue

        # CASE: Characters have entered
        # Get character names, add coappearances, update current character list
        elif 'Enter' in result:

            # Find all proper nouns (characters) in result
            chars = re.findall('[A-Z][a-z]+', result.strip('Enter').strip())

            # CASE: fairies
            if result == 'Enter four Fairies.':
                fairies = ['Peaseblossom', 'Cobweb', 'Moth', 'Mustardseed']
                all_appearances = add_coappear(curr_char, fairies,
                                               all_appearances, scene,
                                               int_cast_dict)
                curr_char.extend(fairies)

            # CASE: all other characters
            else:
                all_appearances = add_coappear(curr_char, chars,
                                               all_appearances, scene,
                                               int_cast_dict)
                curr_char.extend(chars)

        # CASE: someone is speaking
        elif re.match('[A-Z]+\.', result):

            # New speaker, save current speaker as previous speaker
            if curr_speak != '':
                prev_speak = curr_speak

            curr_speak = result.strip('.').title()

            # If they are speaking then they could not still be asleep
            # Update sleeping list
            if curr_speak in asleep:
                asleep.remove(curr_speak)

        # CASE: exit without specified character, assume is curr_speak
        elif result == 'Exit.':

            # CASE: actors in play within play exit
            if curr_speak not in curr_char:
                actor = ''
                if curr_speak in int_cast_dict.keys():
                    actor = int_cast_dict[curr_speak]
                    curr_char.remove(actor)

                else:
                    print('WE HAVE A PROBLEM HERE.')

            # CASE: all other characters, assume curr_speak exits
            else:
                curr_char.remove(curr_speak)

        # CASE: exeunt without specified characters, assume all conscious
        #       characters exit
        elif result == 'Exeunt.':
            to_exit = [char for char in curr_char if char not in asleep]

            for char in to_exit:
                curr_char.remove(char)

        # CASE: specified characters exit
        elif (('Exit' in result) | ('Exeunt' in result)) & ('all but' not in result):

            # CASE: someone exits and someone sleeps in same stage direction
            if 'sleep' in result:
                stage_dir = result.split('. ')

                for dir_ in stage_dir:

                    # First half of direction, get those who exit
                    if 'Exeunt' in dir_:
                        chars = re.findall('[A-Z][a-z]+',
                                dir_.strip('Exeunt').strip())
                        for char in chars:
                            if (char == 'Fairies'):
                                if 'Fairies' in curr_char:
                                    curr_char.remove('Fairies')
                                elif 'Train' in curr_char:
                                    curr_char.remove('Train')

                    # Get other part of direction where someone sleeps
                    elif 'sleep' in dir_:
                        chars = re.findall('[A-Z][a-z]+', dir_)
                        for char in chars:
                            asleep.extend([char])

            # CASE: all other exit cases
            # Find characters in stage direction, update current character list
            else:
                chars = re.findall('[A-Z][a-z]+',
                        result.strip('Exit').strip().strip('Exeunt').strip())

                for char in chars:

                    # Stage directions interchangeably refer to Fairies and Trains
                    if (char == 'Fairies'):
                        if 'Fairies' in curr_char:
                            curr_char.remove('Fairies')

                        elif 'Train' in curr_char:
                            curr_char.remove('Train')

                    # Stage directions will interchangeably refer to clowns
                    elif char == 'Clowns':
                        for actor in ['Flute', 'Snout', 'Starveling', 'Quince', 'Snug']:
                            if actor in curr_char:
                                curr_char.remove(actor)

                    # CASE: just because one attendant leaves does not mean all
                    #       attendants leave
                    elif char == 'Attendant':
                        continue

                    # CASE: all other exits, just remove the character
                    else:
                        curr_char.remove(char)

        # CASE: exeunt all but, remove all current characters except those in
        #       stage direction
        elif 'Exeunt all but' in result:
            chars = re.findall('[A-Z][a-z]+', result.strip('Exeunt all but').strip())
            curr_char = [char for char in curr_char if char in chars]

        # CASE: sleep without specified character, assumes current speaker sleeps
        elif ('Sleeps.' in result) | ('Lies down and sleeps.' in result):
            asleep.extend([curr_speak])

        # CASE: assume that they refers to current speaker and previous speaker
        elif 'They sleep' in result:
            asleep.extend([curr_speak])
            asleep.extend([prev_speak])

    return all_appearances
