# def card_info(request, card_code: str) -> HttpResponse:
#     if (card_queryset := CardInfo.objects.filter(card_code=card_code)).exists():
#         card_info = card_queryset.first()
#     else:
#         arkhamdb_card_info = retrieve_card_info_from_arkhamdb(card_code)
#     CardInfo.objects.get_or_create()
#     # return HttpResponse(retrieve_card_info(card_code))
#     return render(request, "cards.html", {"cards": [retrieve_card_info_from_arkhamdb(card_code)]})
