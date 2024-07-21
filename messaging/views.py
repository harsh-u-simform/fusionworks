from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from messaging.src.langchain_helper import LangchainHelper

class AskMe(APIView):

    def get(self, request, format=None):
        """
        Process the user prompt
        """

        try:
            response = LangchainHelper().process_propt(request)
        except BaseException as e:
            print(e)
            response = {
                "response": "Sorry for inconvenience. Currenly we are unable to find the answer of your query.",
            }

        return Response({
            'data': response,
        })
    