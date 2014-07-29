#-*- coding: utf8-*-

import os.path
import sys
import argparse
import urllib, json
from pyunimarc import Record, MARCWriter, MARCWriter2, Field
import pdb
# Documentation complète et à jour sur le format Unimarc
# http://www.bnf.fr/fr/professionnels/anx_formats/a.unimarc_manuel_format_bibliographique.html#SHDC__Attribute_BlocArticle8BnF

#url = 'http://www.preprod.medici.tv/api/movie/?specialview=marcexport&results_limit=100'
url = 'http://www.medici.tv/api/movie/?specialview=marcexport&results_limit=10'

u = urllib.urlopen(url)
data = u.read()

decoded_data = json.loads(data)

if not decoded_data.has_key('results'):
    decoded_data = {"results":[decoded_data]}

from datetime import datetime
date_created = datetime.now()

def as_unimarc():

    for i in range(0, len(decoded_data["results"])):
        filename = 'record-' + str(decoded_data["results"][i]["id"]) + ".mrc"
        writer2 = MARCWriter2(filename)
        record = Record(target="UNIMARC")

        field = Field(tag='001', data='MEDICI-' + str(decoded_data["results"][i]["id"]))
        record.add_field(field)

        field = Field('003', None, None, 'http://www.medici.tv/#?')
        record.add_field(field)

        creation_date = date_created.strftime('%Y%m%d%H%M%S')
        field = Field('005', None, None, creation_date)
        record.add_field(field)

        """
        =100:
        """
        creation_date = date_created.strftime('%Y%m%d')
        publication_date = date_created.strftime('%Y')

        record100 = [' ']*37
        l = list(creation_date)
        record100[0:7] = l
        record100[8] = "i"
        l = list(publication_date)
        record100[9:12]  = l
        record100[22:24] = "EN"
        record100[26:29] = "50"

        field = Field('100', ['#', '#'], ['a', ''.join(record100)])
        record.add_field(field)

        # TODO: codé en dur mais à modifier en fonction des données de la base
        field = Field('101', ['#', '#'], ['a', 'eng', 'd', 'eng'])
        record.add_field(field)

        record135      = [' ']*12
        record135[0]   = "h" # Type de ressource électronique -> j'ai mis "son" mais il y a aussi "i" pour "media interactif"
        record135[1]   = "r" # Type de support utilisé  -> Système en ligne
        record135[2]   = "c" # Couleur -> ici par défaut TODO Alexandre
        record135[3]   = "z" # Dimensions ->z=autre. Dommage
        record135[4]   = "a" # Son -> a=le support contient du son

        field = Field('135', ['#', '#'], ['a', ''.join(record135)])
        record.add_field(field)

        if decoded_data["results"][i]["name"] is None:
            decoded_data["results"][i]["name"] = ''

        field = Field('200', ['1', '#'], ['a', decoded_data["results"][i]["name"].encode("utf-8")])
        record.add_field(field)


        # TODO: bug dans le web service à corriger. Encodage caractère

        if decoded_data["results"][i]["copyright_mention"] is None:
            decoded_data["results"][i]["copyright_mention"] = ''

        tmp = decoded_data["results"][i]["copyright_mention"]

        # Ajouter encode('utf-8') pour éviter les erreurs du type
        # UnicodeEncodeError: 'ascii' codec can't encode character u'\xa9' in position 10: ordinal not in range(128)
        field = Field('210',  ['#', '#'], ['c', tmp.encode('utf-8')])
        try:
            print field.__str__()
            record.add_field(field)
        except UnicodeEncodeError:
            print "Error"


        if decoded_data["results"][i]["duration"] is None:
            decoded_data["results"][i]["duration"] = '0'

        int_duration = int(decoded_data["results"][i]["duration"])/60
        duration = "Online ressource("+ str(int_duration) + ")"

        format_image = decoded_data["results"][i]["format_image"]
        if format_image is None:
            format_image = ''

        field = Field('215', ['#', '#'], ['a', duration, 'd', format_image.encode('utf-8')])
        record.add_field(field)

        if decoded_data["results"][i]["categories"][0] is not None:
            field = Field('608', ['#', '#'], ['a', decoded_data["results"][i]["categories"][0].encode('utf-8')])
            record.add_field(field)

        # Infos casting
        # 700: composer. In case of multiple composer we use 701 field for "Autre responsabilité principale"
        # 100 Marc

        # 701 -> 700
        # 702 -> 700

        # 702: interpreter-physical
        # 712: interpreter-collectivity

        for j in range(0, len(decoded_data["results"][i]["creators"])):

            composer_firstname = decoded_data["results"][i]["creators"][0]['firstname']
            composer_lastname = decoded_data["results"][i]["creators"][0]['lastname']
            function_code_unimarc = decoded_data["results"][i]["creators"][0]['jobs'][0]['function_code_unimarc']


            composer_date_of_birth = decoded_data["results"][i]["creators"][0]['birth_date']
            composer_date_of_death = decoded_data["results"][i]["creators"][0]['death_date']

            if composer_date_of_birth is None:
                composer_date_of_birth = ' '


            if composer_date_of_death is None:
                composer_date_of_death = ' '

            field = Field('700', ['#', '#'], [ 'a', composer_firstname.encode('utf-8'),
                                               'b', composer_lastname.encode('utf-8'),
                                               '4', function_code_unimarc.encode('utf-8')])
            record.add_field(field)

            for k in range(1, len(decoded_data["results"][i]["creators"])):
                composer_firstname = decoded_data["results"][i]["creators"][k]['firstname']
                composer_lastname = decoded_data["results"][i]["creators"][k]['lastname']
                composer_date_of_birth = decoded_data["results"][i]["creators"][k]['birth_date']
                composer_date_of_death = decoded_data["results"][i]["creators"][k]['death_date']
                function_code_unimarc = decoded_data["results"][i]["creators"][k]['jobs'][0]['function_code_unimarc']


                if composer_date_of_birth is None:
                    composer_date_of_birth = ' '


                if composer_date_of_death is None:
                    composer_date_of_death = ' '


                field = Field('701', ['#', '0'], ['a', composer_firstname.encode('utf-8'),
                                                           'b',composer_lastname.encode('utf-8'),
                                                           '4', function_code_unimarc.encode('utf-8')])
                record.add_field(field)


            field = Field('702', ['#', '1'], ['a', composer_firstname.encode('utf-8'),
                                                       'b',composer_lastname.encode('utf-8'),
                                                      'f', composer_date_of_birth.encode('utf-8') + "-" +
                                                           composer_date_of_death.encode('utf-8')]
            )
            record.add_field(field)


        for l in range(0, len(decoded_data["results"][i]["interpreters"]["bands"])):
            collectivity = decoded_data["results"][i]['interpreters']["bands"][l]["lastname"]

            field = Field('712', ['#', '1'], ['a', collectivity.encode('utf-8')])
            record.add_field(field)

        for m in range(0, len(decoded_data["results"][i]["interpreters"]["interpreters"])):
            interpreter_firstname = decoded_data["results"][i]["interpreters"]["interpreters"][m]["firstname"]
            interpreter_lastname = decoded_data["results"][i]["interpreters"]["interpreters"][m]["lastname"]

            tmp = decoded_data["results"][i]["interpreters"]["interpreters"][m]["jobs"]
            if len(tmp) > 0:
                function_code_unimarc = tmp[0]["function_code_unimarc"]

                if function_code_unimarc is not None:
                    field = Field('702', ['#', '1'], [ 'a', interpreter_firstname.encode('utf-8'),
                                                       'b', interpreter_lastname.encode('utf-8'),
                                                       '4', function_code_unimarc.encode('utf-8')
                    ])
                    record.add_field(field)
            else:
                field = Field('702', ['#', '1'], [ 'a', interpreter_firstname.encode('utf-8'),
                                                       'b', interpreter_lastname.encode('utf-8'),
                ])


        for n in range(0, len(decoded_data["results"][i]["director"])):
            moviedirector_firstname = decoded_data["results"][i]["director"][n]["firstname"]
            moviedirector_lastname = decoded_data["results"][i]["director"][n]["lastname"]
            function_code_unimarc = decoded_data["results"][i]["director"][n]["jobs"][0]["function_code_unimarc"]

            field = Field('702', ['#', '1'], ['a', moviedirector_firstname.encode('utf-8'),
                                               'b', moviedirector_lastname.encode('utf-8'),
                                               '4', function_code_unimarc.encode('utf-8')])
            record.add_field(field)


        # UNIMARC = MARC21 : 856: Electronic location and address
        field = Field('856', ['#', '#'], ['u', "http://www.medici.tv/"])
        record.add_field(field)

        # Attention fait parfois planter le pg
        # a cause d'une erreur unicode
        #print record

        writer2.write(record)

def main():
    as_unimarc()

if __name__ == '__main__':
    main()