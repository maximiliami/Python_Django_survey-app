from questionnaire.models import PseudoUser, Pair


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
