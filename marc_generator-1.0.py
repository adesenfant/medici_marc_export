#-*- coding: utf8-*-

import os.path
import sys
import argparse
import pyunimarc
from pyunimarc.exceptions import FileNotFoundException
from pyunimarc.constants import SEP, SP, BLANK, BACKSLASH
from notice_dictionary import FR_MEDICI_UNIMARC_FUNCTION_CODES_MAPPING
from pyunimarc import MRCWriter
import urllib, json
import pymarc

# Documentation complète et à jour sur le format Unimarc
# http://www.bnf.fr/fr/professionnels/anx_formats/a.unimarc_manuel_format_bibliographique.html#SHDC__Attribute_BlocArticle8BnF

url = 'http://www.preprod.medici.tv/api/movie/?specialview=marcexport&results_limit=20'

u = urllib.urlopen(url)
data = u.read()

decoded_data = json.loads(data)

def dict2file(outputFile):
    str_sep = BACKSLASH*2
    output = open(outputFile, 'w')

    # Identificateur de la notice attribué par Medici.
    # Cet identificateur peut prendre n'importe quelle forme.
    # Dans le cas de Medici, toutes les notices seront préfixées
    # par le trigramme MED auquel on ajoute l'identifiant de la
    # base de données.

    print "Number of notices to produce:", len(decoded_data["results"])

    from datetime import datetime
    date_created = datetime.now()

    for i in range(0, len(decoded_data["results"])):
        print decoded_data["results"][i]["id"]

        output.write("=LDR  "  + "ngm 22  9 4500" + "\n")
        output.write("=001  MEDICI-"+ str(decoded_data["results"][i]["id"]) +"\n")
        #output.write("=002  " + str_sep + "\n")
        output.write("=003  " + "http://www.medici.tv/#?" + "\n")

        # 16 caractères indiquant la date/heure de la dernière mise à jour de la notice
        # 4 pour l'année, 2 pour le mois, 2 pour le jour, 2 pour l'heure, 2 pour la minute, 2 pour la seconde
        # 2 pour le dixième de seconde avec le point indiquant la décimale
        creation_date = date_created.strftime('%Y%m%d%H%M%S')
        output.write("=005  " + creation_date + ".000" + "\n")

        # 100 Données générales de traitement

        creation_date = date_created.strftime('%Y%m%d')
        publication_date = date_created.strftime('%Y')

        record101 = [SP]*36
        l = list(creation_date)
        record101[0:7] = l
        record101[8] = SP
        l = list(publication_date)
        record101[9:12] = l
        record101[13:16] = SP*4
        record101[17:19] = SP
        record101[20] = SP
        record101[21] = SP
        record101[22:24] = "EN"
        record101[25] = SP
        record101[26:29] = "50"
        record101[30:33] = SP*2
        record101[34:35] = SP*4

        output.write("=100  " + str_sep + "$a" + ''.join(record101) + "\n")

        output.write("=101  " + "0" + BACKSLASH + "$a"+ "eng" + "$d" + "eng" + "\n")

        record135      = [SP]*12
        record135[0]   = "h" # Type de ressource électronique -> j'ai mis "son" mais il y a aussi "i" pour "media interactif"
        record135[1]   = "r" # Type de support utilisé  -> Système en ligne
        record135[2]   = "c" # Couleur -> ici par défaut
        record135[3]   = "z" # Dimensions ->z=autre. Dommage
        record135[4]   = "a" # Son -> a=le support contient du son
        record135[5:6] = SP  # Nombre de bits par pixel
        record135[7]   = SP  # Nombre de formats
        record135[8]   = SP  # Qualité recherchée
        record135[9]   = SP   # Source
        record135[10]  = SP  # Compression
        record135[11]  = SP  # Qualité de reformatage

        output.write("=135  " + str_sep + "$a" + ''.join(record135) + "\n")
        # Boucle sur les formats
        #output.write("=135  " + str_sep + "$a"+ new_dict['format_color'] + "\n")
        #output.write("=135  " + str_sep + "$a"+ decoded_data["results"][i]["format_image"] + "\n")
        #output.write("=135  " + str_sep + "$a"+ new_dict['format_quality']+ "\n")

        output.write("=200  " + "1"+ BACKSLASH + "$a"+ decoded_data["results"][i]["name"] + "\n")

        output.write("=210  " + str_sep + "$c"+ decoded_data["results"][i]["copyright_mention"].encode('utf-8') + "\n")

        int_duration = int(decoded_data["results"][i]["duration"])/60
        my_str = str(int_duration)
        output.write("=215  " + str_sep + "$a1" + "Online ressource(" + my_str + ")" + "$d" + decoded_data["results"][i]["format_image"] + "\n")


        if(decoded_data["results"][i]["synopsis_marc"] != None):
            output.write("=300  " + str_sep + "$a" + decoded_data["results"][i]["synopsis_marc"]+ "\n")

        #Movie category
        output.write("=608  " + str_sep + "$a" + decoded_data["results"][i]["categories"][0]+ "\n")

        # Infos casting
        # 700: composer. In case of multiple composer we use 701 field for "Autre responsabilité principale"
        # 702: interpreter-physical
        # 712: interpreter-collectivity

        for j in range(0, len(decoded_data["results"][i]["creators"])):

            composer_firstname = decoded_data["results"][i]["creators"][0]['firstname']
            composer_lastname = decoded_data["results"][i]["creators"][0]['lastname']
            composer_date_of_birth = decoded_data["results"][i]["creators"][0]['birth_date']
            composer_date_of_death = decoded_data["results"][i]["creators"][0]['death_date']

            function_code = FR_MEDICI_UNIMARC_FUNCTION_CODES_MAPPING["Compositeur"]

            output.write("=700  "
                         + str_sep
                         + "0"
                         + "$a" + composer_firstname.encode('utf-8')
                         + "$b" + composer_lastname.encode('utf-8')
                         + "$4" + function_code + "\n")

            for k in range(1, len(decoded_data["results"][i]["creators"])):
                composer_firstname = decoded_data["results"][i]["creators"][k]['firstname']
                composer_lastname = decoded_data["results"][i]["creators"][k]['lastname']
                composer_date_of_birth = decoded_data["results"][i]["creators"][k]['birth_date']
                composer_date_of_death = decoded_data["results"][i]["creators"][k]['death_date']

                output.write("=701  "
                             + str_sep
                             + "0"
                             + "$a" + composer_firstname.encode('utf-8')
                             + "$b" + composer_lastname.encode('utf-8')
                             + "$4" + function_code + "\n")


            output.write("=702  " + str_sep + "1" + "$a" + composer_firstname + "$b" + composer_lastname + "$f"
                         + composer_date_of_birth + "-" + composer_date_of_death+ "\n")


        for l in range(0, len(decoded_data["results"][i]["interpreters"]["bands"])):
            collectivity = decoded_data["results"][i]['interpreters']["bands"][l]["lastname"]
            output.write("=712  " + str_sep + "1" + "$a" + collectivity + "\n")

        for m in range(0, len(decoded_data["results"][i]["interpreters"]["interpreters"])):

            job = ""

            if(len(decoded_data["results"][i]["interpreters"]["interpreters"][m]["jobs"])>0):
                print decoded_data["results"][i]["interpreters"]["interpreters"][m]["jobs"][0]
                job = decoded_data["results"][i]["interpreters"]["interpreters"][m]["jobs"][0]["name_fr"]
                print job

            # TODO : tester si le job est présent dans l'extraction et mettre $4 sinon ne rien mettre
            interpreter_firstname = decoded_data["results"][i]["interpreters"]["interpreters"][m]["firstname"]
            interpreter_lastname = decoded_data["results"][i]["interpreters"]["interpreters"][m]["lastname"]

            output.write("=702  "
                         + str_sep
                         + "1"
                         + "$a" + interpreter_firstname.encode('utf-8')
                         + "$b"  + interpreter_lastname.encode('utf-8')
                         #+ "$4"  + FR_MEDICI_UNIMARC_FUNCTION_CODES_MAPPING[job]
                         + "\n")


        for n in range(0, len(decoded_data["results"][i]["director"])):
            moviedirector_firstname = decoded_data["results"][i]["director"][n]["firstname"]
            moviedirector_lastname = decoded_data["results"][i]["director"][n]["lastname"]
            output.write("=702  "
                         + str_sep
                         + "1"
                         + "$a"
                         + moviedirector_firstname.encode('utf-8')
                         + "$b"
                         + moviedirector_lastname.encode('utf-8')
                         + "$4" + "300"
                         + "\n")

        # Lien url
        output.write("=856  " + "4" + BACKSLASH + "$u" + "http://www.medici.tv/" + "\n")
        output.write("\n")

def main():
    dict2file('mnemonic.dat')

if __name__ == '__main__':
    main()