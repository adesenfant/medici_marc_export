# -*- coding: utf8-*-

import os.path
import sys
import argparse
import urllib, json, logging, time
from pyunimarc import Record, MARCWriter, MARCWriter2, Field
import pdb
# Documentation complÃ¨te et Ã  jour sur le format Unimarc
# http://www.bnf.fr/fr/professionnels/anx_formats/a.unimarc_manuel_format_bibliographique.html#SHDC__Attribute_BlocArticle8BnF

# url = 'http://www.medici.tv/api/movie/?specialview=marcexport&results_limit=100'
#
# u = urllib.urlopen(url)
# data = u.read()
#
# decoded_data = json.loads(data)
#
# if not decoded_data.has_key('results'):
#     decoded_data = {"results":[decoded_data]}


def as_marc21(decoded_data):

    from datetime import datetime
    date_created = datetime.now()

    for i in range(0, len(decoded_data["results"])):

        creators = decoded_data["results"][i]["creators"]
        bands = decoded_data["results"][i]["interpreters"]["bands"]
        interpreters = decoded_data["results"][i]["interpreters"]["interpreters"]
        directors = decoded_data["results"][i]["director"]

        filename = 'export/record-' + str(decoded_data["results"][i]["id"]) + ".mrc-marc8"
        #filename = 'export/record-' + str(decoded_data["results"][i]["id"]) + ".mrc-utf8"
        writer2 = MARCWriter2(filename)
        record = Record(target=u'MARC21')

        field = Field(tag=u'001', data=u'MEDICI-' + str(decoded_data["results"][i]["id"]))
        record.add_field(field)

        field = Field(u'003', None, None, u'medici.tv')
        record.add_field(field)

        creation_date = date_created.strftime(u'%Y%m%d%H%M%S')
        field = Field(u'005', None, None, creation_date)
        record.add_field(field)

        # Fixed-Length Data Elements-Additional Material Characteristics
        field = Field(tag=u'006', data=u'm||||||||c||||||||')
        record.add_field(field)

        # Fixed-Length Data Elements-Additional Material Characteristics
        field = Field(tag=u'007', data=u'cr||n|---||a|a')
        record.add_field(field)

        # Fixed-Length Data Elements-Additional Material Characteristics
        field = Field(tag=u'007', data=u'vz||zazu|')
        record.add_field(field)

        # UNIMARC 100 --> MARC21 008
        creation_date = date_created.strftime(u'%y%m%d')
        publication_date = date_created.strftime(u'%Y')

        record008 = [' ']*38
        l = list(creation_date)
        record008[0:5] = l
        record008[6] = u"p"
        l = list(publication_date)
        record008[7:10]  = l

        field = Field(tag=u'008', data=u''.join(str(e) for e in record008))
        record.add_field(field)

        # Transfer UNIMARC 100 22-24 LANGUAGE OF CATALOGING TO MARC 040
        field = Field(u'040', [' ', ' '], [u'b', u'EN'])
        record.add_field(field)

        # Langue : 101 (UNI) - 041 (M21)
        field = Field(u'041', [' ', ' '], [u'a', u'eng', u'd', u'eng'])
        record.add_field(field)


        # UNIMARC 700 -> MARC21 100
        champ100present=0
        stars = decoded_data["results"][i]["stars"]
        if len(stars)>0:
            field = Field('100', ['1', ' '], [ 'a', stars[0]['lastname'].decode('utf-8') + ', ' + stars[0]['firstname'].decode('utf-8')])
            record.add_field(field)
            champ100present=1

        #title_marc
        title_marc=decoded_data["results"][i]["title_marc"]
        if title_marc is None:
            title_marc = ''
        else:
            title_marc = title_marc.decode('utf-8')
        field = Field(u'245', [champ100present, decoded_data["results"][i]["title_marc_index"]], ['a', title_marc ,'h','[electronic resource]'])
        record.add_field(field)

        # TODO: bug dans le web service Ã  corriger. Encodage caractÃ¨re
        tmp = decoded_data["results"][i]["copyright_mention"].decode('utf-8')
        #tmp=tmp.replace(u"\u00A9",'cop.')

        # Adresse biblio : 210 (UNI) - 260 (M21) - attention sous-zones diffÃ©rentes
        field = Field(u'260',  [' ', ' '], ['b', tmp])
        record.add_field(field)

        int_duration = int(decoded_data["results"][i]["duration"])/60
        duration = u" 1 streaming video file ("+ str(int_duration) + u" min.)"

        #Collation : 215 (UNI) - 300 (M21)
        format_image = decoded_data["results"][i]["format_image"]
        if format_image:
            field = Field('300', [' ', ' '], ['a', duration, 'c', format_image.decode('utf-8')])
            record.add_field(field)
        else:
            field = Field('300', [' ', ' '], ['a', duration])
            record.add_field(field)

        field = Field(u'506', ['1', ' '], [ 'a', u'Access restricted to subscribers.'])
        record.add_field(field)

        field = Field(u'520', [' ', ' '], [ 'a', decoded_data["results"][i]["synopsis_marc"].decode('utf-8')])
        record.add_field(field)

        # Indexation genre : 608 (UNI) - 655 (M21)
        field = Field('655', [' ', '4'], ['a', decoded_data["results"][i]["categories"][0].decode('utf-8')])
        record.add_field(field)

        # Infos casting
        # 700: composer. In case of multiple composer we use 701 field for "Autre responsabilitÃ© principale"
        # 702: interpreter-physical
        # 712: interpreter-collectivity

        for k in range(1, len(creators)):


            composer_firstname = creators[k]['firstname'].decode('utf-8')
            composer_lastname = creators[k]['lastname'].decode('utf-8')

            jobs = creators[k]['jobs']

            function_code_marc21 = None
            if jobs:
                if jobs[0]['function_code_marc21']:
                    function_code_marc21 = jobs[0]['function_code_marc21'].decode('utf-8')

            # UNIMARC 702 -> MARC21 700
            composer_date_of_birth = None
            composer_date_of_death = None
            if composer_lastname and composer_firstname:
                if creators[k]['birth_date']:
                        composer_date_of_birth = creators[k]['birth_date'].decode('utf-8')
                else:
                    composer_date_of_birth = ' '

                if creators[k]['death_date']:
                    composer_date_of_death = creators[k]['death_date'].decode('utf-8')
                else:
                    composer_date_of_death = ' '
            fonction = ['a', composer_lastname + ', ' + composer_firstname]
            if function_code_marc21:
                fonction += ['4', function_code_marc21]

            if composer_date_of_birth and composer_date_of_death:
                fonction += ['d', composer_date_of_birth + "-" + composer_date_of_death]

            field = Field('700', ['1', ' '], fonction)
            record.add_field(field)


        for l in range(0, len(decoded_data["results"][i]["interpreters"]["bands"])):
            collectivity = decoded_data["results"][i]['interpreters']["bands"][l]["lastname"].decode('utf-8')

            # UNIMARC 712 -> MARC21 710
            field = Field('710', ['2', ' '], ['a', collectivity])
            record.add_field(field)

        for m in range(0, len(interpreters)):
            interpreter_firstname = interpreters[m]["firstname"]
            interpreter_lastname = interpreters[m]["lastname"]

            if interpreter_firstname and interpreter_lastname:
                function_code_marc21 = None
                if len(interpreters[m]["jobs"])>0:
                    function_code_marc21 = interpreters[m]["jobs"][0]["function_code_marc21"]

                if len(interpreters[m]["instruments"])>0:
                    function_code_marc21 = interpreters[m]["instruments"][0]["function_code_marc21"]

                if function_code_marc21 is not None:
                    field = Field('700', ['1', ' '], [ 'a', interpreter_lastname.decode('utf-8') + ', '
                                                                + interpreter_firstname.decode('utf-8'),
                                                           '4', function_code_marc21.decode('utf-8')

                        ])
                    record.add_field(field)
                else:
                    field = Field('700', ['3', ' '], [ 'a', interpreter_lastname.decode('utf-8') + ', '
                                                            + interpreter_firstname.decode('utf-8')])
                    record.add_field(field)

        for n in range(0, len(directors)):
            moviedirector_firstname = directors[n]["firstname"]
            moviedirector_lastname = directors[n]["lastname"]

            if moviedirector_firstname and moviedirector_lastname:
                if len(directors[n]["jobs"])>0:
                    function_code_marc21 = directors[n]["jobs"][0]["function_code_marc21"]
                    if function_code_marc21 is not None:
                        field = Field('700', ['1', ' '], ['a', moviedirector_lastname.decode('utf-8') + ', ' +
                                                               moviedirector_firstname.decode('utf-8'),
                                                           '4', function_code_marc21.decode('utf-8')])
                        record.add_field(field)


        # 856: Lien url
        field = Field('856', ['4', '0'], ['u', "http://www.medici.tv/#!/"+decoded_data["results"][i]["slug"].decode('utf-8')])
        record.add_field(field)

        writer2.write(record)


def main():

    url = 'http://www.medici.tv/api/movie/?is_free=0&type=c&status_en=o&page=1&page_size=1'
    u = urllib.urlopen(url)
    data = u.read()
    monjson = json.loads(data)
    try:
        nbFilms = int(monjson["count"])
    except:
        nbFilms = 1
    logging.basicConfig(filename='marcexport.log',level=logging.DEBUG)

    #film_list = [3,22,37,39,87,91,279,452,507,537,617,1142,1711,1863,2305]

    for f in range(1, nbFilms+1):
    #for FilmIndex in film_list:
        ok=False
        while not ok:
            url = 'http://www.medici.tv/api/movie/?is_free=0&type=c&status_en=o&specialview=marcexport&page='+ str(f) +'&page_size=1'
            #507, 1142, 1711, 1863,2305
            #url = 'http://www.medici.tv/api/movie/'+str(FilmIndex)+'/?specialview=marcexport'
            u = urllib.urlopen(url)
            data = u.read()
            try:
                monjson = json.loads(data)
            except:
                # Wait for 1 seconds
                time.sleep(1)
                break
            ok = True
        if not monjson.has_key('results'):
            monjson = {"results":[monjson]}
        film=monjson["results"][0]["id"]
        #if film>700:
        #    continue
        try:
            as_marc21(monjson)
            logging.info('Film '+ str(film) +' OK')
        except Exception as inst:
            logging.warning('Film '+ str(film)+' KO : '+inst.__str__())

if __name__ == '__main__':
    main()
