import csv
import datetime
import itertools
import os

from django.shortcuts import HttpResponse
from questionnaire.models import PseudoUser, Pair, QuestionnaireDaily


class Service:
    PERIOD = 60

    # gets a querylist of pairs wich not have two participants
    @staticmethod
    def get_open_pairs():
        query_set = []
        member_count = 0
        for pair in Pair.objects.all():
            for user in PseudoUser.objects.all():
                if user.pair == pair:
                    member_count += 1
            if member_count < 2:
                query_set.append(pair)
            member_count = 0

        return Pair.objects.filter(ident__in=query_set)

    @staticmethod
    def db_checkup():
        for user in PseudoUser.objects.all():
            has_dq_for_today = False
            print(user)
            if QuestionnaireDaily.objects.filter(pseudo_user=user) < Service.PERIOD:
                for dq in QuestionnaireDaily.objects.filter(pseudo_user=user):
                    print(dq)
                    if dq.date.date() == datetime.date.today():
                        has_dq_for_today = True
                if not has_dq_for_today:
                    new_dq = QuestionnaireDaily()
                    new_dq.pseudo_user = user
                    new_dq.save()
                print(has_dq_for_today)

        f = open(os.environ['HOME'] + '/db_checkup.txt', 'w')
        f.write(f'Die DB wurde um:{str(datetime.datetime.now())} Uhr geprüft')
        f.close()

    @staticmethod
    def download_data_service(pk):

        if pk is None:
            pairs = Pair.objects.all()
            data_name = 'data'
        else:
            pairs = Pair.objects.filter(pk=pk)
            data_name = pairs.get(pk=pk).ident

        this_response = HttpResponse(
            content_type='text/csv',
            headers={f'Content-Disposition': f'attachment; filename="Zyklus-qpp-{data_name}.csv"'},
        )
        writer = csv.writer(this_response)

        pseudo_users = PseudoUser.objects.all()
        daily_questionnaires = QuestionnaireDaily.objects.all()

        for pair in pairs:
            pair_users = pseudo_users.filter(pair=pair)
            print(f'pair_users = {pair_users.count()}')
            if pair_users.count() == 2:
                pair_user_one = pair_users[0]
                pair_user_two = pair_users[1]

                pair_user_one_questionnaires = daily_questionnaires.filter(pseudo_user__exact=pair_user_one)
                pair_user_two_questionnaires = daily_questionnaires.filter(pseudo_user__exact=pair_user_two)

                writer.writerow(
                    ['Pärchen', 'Benutzer1', 'Datum DailyQuestionnaire', f'F1 P1 {pair_user_one.gender}',
                     f'F2 P1 {pair_user_one.gender}',
                     f'F3 P1 {pair_user_one.gender}',
                     f'F4 P1 {pair_user_one.gender}', f'F5 P1 {pair_user_one.gender}',
                     f'F6 P1 {pair_user_one.gender}',
                     'Benutzer2', 'Datum DailyQuestionnaire',
                     f'F1 P2 {pair_user_two.gender} ', f'F2 P2 {pair_user_two.gender}',
                     f'F3 P2 {pair_user_two.gender}',
                     f'F4 P2 {pair_user_two.gender}', f'F5 P2 {pair_user_two.gender}',
                     f'F6 P2 {pair_user_two.gender}'])

                for (dq_user_one, dq_user_two) in itertools.zip_longest(pair_user_one_questionnaires,
                                                                        pair_user_two_questionnaires):
                    print(f'(Ausgangswert: {dq_user_one}, {dq_user_two})')
                    if dq_user_one is None:
                        dq_user_one = QuestionnaireDaily(pseudo_user=PseudoUser(user_code='Default'))
                        dq_user_one.date = datetime.datetime.today()
                        dq_user_one.question_one = 'Kein Wert'
                        dq_user_one.question_two = 'Kein Wert'
                        dq_user_one.question_three = 'Kein Wert'
                        dq_user_one.question_four = 'Kein Wert'
                        dq_user_one.question_five = 'Kein Wert'
                        dq_user_one.question_six = 'Kein Wert'
                    if dq_user_two is None:
                        dq_user_two = QuestionnaireDaily(pseudo_user=PseudoUser(user_code='Default'))
                        dq_user_two.date = datetime.datetime.today()
                        dq_user_two.question_one = 'Kein Wert'
                        dq_user_two.question_two = 'Kein Wert'
                        dq_user_two.question_three = 'Kein Wert'
                        dq_user_two.question_four = 'Kein Wert'
                        dq_user_two.question_five = 'Kein Wert'
                        dq_user_two.question_six = 'Kein Wert'

                    print(f'({dq_user_two}, {dq_user_one})')
                    writer.writerow([pair.ident, pair_user_one.user_code, dq_user_one.date.date(),
                                     dq_user_one.question_one, dq_user_one.question_two, dq_user_one.question_three,
                                     dq_user_one.question_four, dq_user_one.question_five, dq_user_one.question_six,
                                     pair_user_two.user_code, dq_user_two.date.date(), dq_user_two.question_one,
                                     dq_user_two.question_two, dq_user_two.question_three,
                                     dq_user_two.question_four,
                                     dq_user_two.question_five, dq_user_two.question_six])

        return this_response
