import csv
import datetime
import itertools
import os

from django.shortcuts import HttpResponse, render, redirect
from webpush import send_group_notification
from django.contrib.contenttypes.models import ContentType

from questionnaire.models import PseudoUser, Pair, Question, QuestionCatalogue, Questionnaire, Answer


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
            print(f'User: {user}')
            if Questionnaire.objects.filter(pseudo_user__exact=user,
                                            is_end_questionnaire=False,
                                            is_start_questionnaire=False).count() < Service.PERIOD:
                for dq in Questionnaire.objects.filter(pseudo_user__exact=user,
                                                       is_end_questionnaire=False,
                                                       is_start_questionnaire=False):
                    print(f'Daily-questionnaire: {dq.date.date()}')
                    if dq.date.date() == datetime.date.today():
                        print(f'dq-date: {dq.date.date()}, date today: {datetime.date.today()}')
                        has_dq_for_today = True

                if not has_dq_for_today:
                    new_dq = Questionnaire()
                    new_dq.pseudo_user = user
                    new_dq.save()
                    question_catalogue = QuestionCatalogue.objects.filter(name__exact='daily')
                    questions = QuestionCatalogue.get_all_questions(question_catalogue[0])
                    for question in questions:
                        answer = Answer(pseudo_user=user,
                                        value=10,
                                        answer_text='Automatisch generiert',
                                        questionnaire=new_dq)
                        answer.save()
                print(has_dq_for_today)

        f = open(os.environ['HOME'] + '/db_checkup.txt', 'w')
        f.write(f'Die DB wurde um:{str(datetime.datetime.now())} Uhr gepr??ft')
        f.close()

    @staticmethod
    def download_data_service(pk):

        question_catalogue = QuestionCatalogue.objects.filter(name__exact='daily')
        questions = QuestionCatalogue.get_all_questions(question_catalogue[0])
        question_list = []
        headline_user_one = ['P??rchen', 'Benutzer 1', 'Datum']
        headline_user_two = ['Benutzer 2', 'Datum']
        headline = []

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
        daily_questionnaires = Questionnaire.objects.filter(is_end_questionnaire=False, is_start_questionnaire=False)

        for pair in pairs:
            pair_users = pseudo_users.filter(pair=pair)
            print(f'pair_users = {pair_users.count()}')
            if pair_users.count() == 2:
                pair_user_one = pair_users[0]
                pair_user_two = pair_users[1]

                pair_user_one_questionnaires = daily_questionnaires.filter(pseudo_user__exact=pair_user_one)
                pair_user_two_questionnaires = daily_questionnaires.filter(pseudo_user__exact=pair_user_two)

                print(f'Questions: {questions}')

                for question in questions:
                    question_list.append(question.name)
                    print(f'Question_Text: {question.question_text}')

                for e in headline_user_one:
                    headline.append(e)
                for e in question_list:
                    headline.append(e)
                for e in headline_user_two:
                    headline.append(e)
                for e in question_list:
                    headline.append(e)
                question_list.clear()

                print(f'Headline:{headline}')

                writer.writerow(headline)
                headline.clear()

                for (dq_user_one, dq_user_two) in itertools.zip_longest(pair_user_one_questionnaires,
                                                                        pair_user_two_questionnaires):

                    # TODO auslagern in Methode
                    answer_list_user_one = []
                    answer_list_user_two = []
                    line = []

                    # TODO Questionnaire hat keine Antworten
                    print(f'(Ausgangswert: {dq_user_one}, {dq_user_two})')
                    if dq_user_one is None:
                        dq_user_one = Questionnaire(pseudo_user=PseudoUser(user_code='Default'))
                        dq_user_one.date = datetime.datetime.today()
                        for question in question_list:
                            answer_list_user_one.append('Automatisch generiert')
                    else:
                        answers = Answer.objects.filter(questionnaire=dq_user_one)
                        for answer in answers:
                            answer_list_user_one.append(answer.value)
                    data_list_user_one = [pair.ident, pair_user_one.user_code, dq_user_one.date.date()]

                    if dq_user_two is None:
                        dq_user_two = Questionnaire(pseudo_user=PseudoUser(user_code='Default'))
                        dq_user_two.date = datetime.datetime.today()
                        for question in question_list:
                            answer_list_user_two.append('Automatisch generiert')
                    else:
                        answers = Answer.objects.filter(questionnaire=dq_user_two)
                        for answer in answers:
                            answer_list_user_two.append(answer.value)
                    data_list_user_two = [pair_user_two.user_code, dq_user_two.date.date()]

                    for e in data_list_user_one:
                        line.append(e)
                    for e in answer_list_user_one:
                        line.append(e)
                    for e in data_list_user_two:
                        line.append(e)
                    for e in answer_list_user_two:
                        line.append(e)

                    print(f'line: {line}')

                    writer.writerow(line)
                    line.clear()

        return this_response

    @staticmethod
    def notify_via_webpush():
        payload = {"head": "Erinnerung",
                   "body": "Hast du deinen Fragebogen heute bereits ausgef??llt?",
                   "icon": "/static/images/lotus.png",
                   "url": "https://zyklus-app.project.mylab.th-luebeck.de/"}
        send_group_notification("daily", payload=payload, ttl=1000)

    @staticmethod
    def get_question_catalogue_id(lookup):
        questionnaire_catalogue = QuestionCatalogue.objects.filter(which_questionnaire=lookup)
        try:
            questionnaire_catalogue_exact = questionnaire_catalogue[0].id
        except IndexError:
            return redirect('questionnaire/success.html')
        return questionnaire_catalogue_exact

    @staticmethod
    def get_questions_for_catalogue_by_id(request, questionnaire_catalogue_id):
        try:
            questionnaire_catalogue = ContentType.objects.get_for_model(QuestionCatalogue)
            questions = Question.objects.filter(content_type__pk=questionnaire_catalogue.id,
                                                object_id__exact=questionnaire_catalogue_id)
        except IndexError:
            return render(request, 'questionnaire/success.html')

        return questions
