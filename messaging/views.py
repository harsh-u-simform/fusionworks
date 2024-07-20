from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from messaging.src.langchain_helper import LangchainHelper

class AskMe(APIView):

    def get(self, request, format=None):
        """
        Process the user promt
        """

        response = LangchainHelper().process_propt(request)

        return Response({
            'data': response,
        })
    