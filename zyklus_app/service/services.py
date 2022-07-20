import datetime
import os
from questionnaire.models import PseudoUser, Pair, QuestionnaireDaily


class Service:

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
    def test_cron():
        # flag = False
        # for user in PseudoUser.objects.all():
        #     for dq in QuestionnaireDaily.objects.filter(pseudo_user__exact=user):
        #         if dq.date == datetime.datetime.today():
        #             flag = True
        # if not flag:
        #     new_dq = QuestionnaireDaily()
        #     new_dq.pseudo_user = user
        #     new_dq.save()

        home = os.environ['HOME']
        f = open(f'{home}/cron_test.txt', 'w')
        f.write(f'Die DB wurde um:{str(datetime.datetime.now())} Uhr geprüft')
        f.close()
