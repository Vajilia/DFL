"""Word pools for character cards: names, hometowns, backgrounds, personalities.

These are PLACEHOLDER flavor lists chosen by the AI so the league has readable people. Nothing in the rules
depends on them. Replace or extend them freely; the card code only needs each list to be non-empty and
the name lists to have no repeats (check_cards.py verifies that).
"""

FIRST_NAMES = """
Aaliyah Abigail Adaeze Adriana Agnes Aiko Alana Alba Alexis Alicia Alina Alma Amara Amelia Amina Ananya
Andrea Angela Anika Anneke Antonia Aria Astrid Ayana Beatriz Bianca Brenna Bridget Britta Brooke Bryn
Camila Candace Carmen Carys Cassidy Catalina Celeste Chiara Chloe Cleo Colette Concetta Corinne Dahlia
Daniela Dara Deja Delphine Destiny Dominique Dorothea Echo Eden Elena Eliana Elise Elsa Emani Emilia
Esme Esperanza Eva Evangeline Fatima Felicity Fiona Freya Gabriela Galina Genevieve Georgia Gianna
Giselle Grace Greta Gwen Hadley Hana Harlow Haruka Hattie Hazel Helena Honor Imani Ines Ingrid Iris
Isabel Isla Ivy Jada Jamila Janelle Jasmine Jelena Jocelyn Josie Juana Julia Junie Kaia Kalani Kamila
Karina Kasey Katya Keisha Kenna Kiara Kimi Kirsten Kora Kyra Lacey Laila Lara Layla Leona Liesel Lila
Linnea Liv Lola Lourdes Luna Lupe Lydia Mabel Maeve Maia Malia Marguerite Maribel Marisol Matilda Maya
Mei Mercy Mika Mila Mirabel Mireya Monique Nadia Naomi Natalia Nia Nina Noor Nova Odalys Olive Oona
Paloma Paulina Penelope Petra Phoebe Priya Quinn Rachelle Rafaela Raina Renata Rhea Rosalind Rosario
Roxanne Ruth Sabine Sadie Samira Saoirse Selah Serena Sienna Signe Simone Sloane Sofia Soledad Stella
Sunny Sylvie Tamsin Tasha Tatiana Teagan Thalia Thea Tilda Tove Treasure Una Valentina Vera Vesper
Vivian Wanda Willa Winona Xiomara Yara Yasmin Yelena Yuki Zadie Zara Zelda Zoe Zuri
""".split()

LAST_NAMES = """
Abara Acosta Adeyemi Aguilar Ahlberg Akana Alderman Alvarado Amundsen Andersen Aoki Arceneaux Ashby Atwood
Avery Baptiste Barlow Barrientos Beaumont Bellamy Benavides Bergstrom Blackwood Boateng Boudreaux Bradshaw
Brandt Briggs Brightwater Brockway Buchanan Burkhart Cabrera Caldwell Calloway Camacho Cardenas Carrow
Castellano Chambers Chandler Chavez Choi Christensen Clairmont Coleridge Colburn Contreras Cordero
Crawley Crenshaw Cruz Dahl Dalton Danforth Davenport Dellinger Delgado Devereux Dietrich Dimitrov Dubois
Duarte Dunmore Eastwood Eberhardt Echeverria Edmonds Eklund Ellison Emerson Enriquez Escobar Espinoza
Everhart Fairbanks Farrow Fennimore Ferreira Fitzgerald Flanagan Fontaine Forsythe Fuentes Gallagher
Galloway Garrison Gaudet Gentry Gillespie Goldberg Gomes Grantham Greer Griffith Guerrero Gunnarsson
Haldane Hallett Hammond Hargrove Haskell Hathaway Hawthorne Hendricks Herrera Hightower Holloway
Holmgren Hutchins Ibarra Iverson Jacobsen Jankowski Jarrett Jefferson Jimenez Jovanovic Kaplan
Kasprzak Kawamoto Keller Kendrick Kimura Kincaid Kirkland Kowalski Kruger Lachance Lambert Landry
Larkin Lazarus Leclair Lindqvist Lockhart Lombardi Lovett Lundgren Macalister Madsen Maldonado Mangum
Marchetti Marlowe Mathis Maynard McAllister McBride Medina Merrick Meyers Mikkelsen Montoya Moreau
Morrow Mulvaney Nakamura Navarro Nettles Nightingale Nolan Novak Oakley Obuya Okafor Olmstead Orozco
Ostrander Paddock Palmieri Pappas Pemberton Peralta Pettigrew Pinkerton Pruitt Quillen Radcliffe
Rasmussen Redfern Reyes Rinaldi Rivas Robeson Rochester Rosales Rourke Rutledge Salazar Sandoval
Saunders Schaefer Sheridan Sinclair Solberg Sorensen Stanhope Stratton Sutherland Tavares Thorne
Tillman Toussaint Trevino Underhill Valdez Vandermeer Vasquez Vickers Villanueva Wagner Waller
Whitlock Winslow Woodruff Yamada Yoder Zamora Zeller Ziegler
""".split()

# Suffixes used when the pool of name pairs is used up (hundreds of seasons away)
NAME_SUFFIXES = ["", " II", " III", " IV", " V", " VI", " VII", " VIII"]

HOMETOWNS = """
Akron OH|Albuquerque NM|Anchorage AK|Atlanta GA|Baton Rouge LA|Birmingham AL|Boise ID|Bozeman MT|Buffalo NY|
Calgary AB|Charleston SC|Cleveland OH|Columbus OH|Compton CA|Corpus Christi TX|Dayton OH|Denver CO|Detroit MI|
Duluth MN|El Paso TX|Fargo ND|Fresno CA|Gary IN|Green Bay WI|Honolulu HI|Houston TX|Indianapolis IN|Jackson MS|
Juneau AK|Kansas City MO|Knoxville TN|Lafayette LA|Laredo TX|Little Rock AR|Louisville KY|Lubbock TX|Memphis TN|
Miami FL|Milwaukee WI|Mobile AL|Montreal QC|Nashville TN|Newark NJ|Oakland CA|Omaha NE|Pago Pago AS|Pittsburgh PA|
Portland OR|Providence RI|Raleigh NC|Reno NV|Richmond VA|Sacramento CA|Salt Lake City UT|San Antonio TX|
Savannah GA|Spokane WA|St. Louis MO|Tacoma WA|Tallahassee FL|Toledo OH|Tulsa OK|Wichita KS|Winnipeg MB|
Youngstown OH|Lagos Nigeria|Monterrey Mexico|Sao Paulo Brazil|Glasgow Scotland|Auckland New Zealand|
Apia Samoa|Accra Ghana|Perth Australia|Dublin Ireland|Helsinki Finland
""".replace("\n", "").split("|")

PATHS = [
    "Power-conference star", "Small-college standout", "Late bloomer", "Walk-on turned starter",
    "International pathway", "Two-sport athlete", "Junior-college transfer", "Overlooked recruit",
    "Coach's daughter", "Came up through the academy system",
]

# core personality -> (what she wants, what she fears)
TRAITS = {
    "Competitor": ("to win everything in front of her", "being outworked"),
    "Loyalist": ("to be a franchise's one-club legend", "being traded or cut"),
    "Mercenary": ("the biggest contract on the market", "a bad deal and an early exit"),
    "Showman": ("the spotlight and a signature moment", "being ignored by the media"),
    "Quiet Leader": ("her teammates' respect", "letting the locker room down"),
    "Hothead": ("to settle every score on the field", "being embarrassed in public"),
    "Perfectionist": ("flawless execution", "the one mistake everyone remembers"),
    "Free Spirit": ("freedom and adventure along the way", "a rigid system"),
    "Grinder": ("to earn every inch", "being handed nothing and losing it anyway"),
    "Diplomat": ("a calm, united team", "locker-room civil war"),
}

TRAIT_NAMES = list(TRAITS)

COACH_PATHS = [
    "Former star player turned coach", "Rose through the assistant ranks", "Small-college head coach promoted",
    "Coordinator who got her first shot", "Came over from another league", "Long-time position coach",
    "Analytics-minded newcomer", "Third-generation coaching family",
]

COACH_TRAITS = {
    "Tactician": ("the cleverest scheme in the league", "being out-schemed on a big night"),
    "Players' Coach": ("a locker room that plays hard for her", "losing the room"),
    "Disciplinarian": ("order, rules and no excuses", "chaos and ego"),
    "Innovator": ("to change how the game is played", "being called old-fashioned"),
    "Survivor": ("another contract year", "the owner's phone call"),
    "Developer": ("to turn raw talent into stars", "wasting a prospect"),
    "Gambler": ("a fourth-down legend", "being second-guessed for the one that failed"),
    "Steady Hand": ("sustained quiet success", "a collapse nobody saw coming"),
}
