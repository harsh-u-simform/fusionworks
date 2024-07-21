from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from messaging.src.langchain_helper import LangchainHelper

class AppHealth(APIView):

    def get(self, request, format=None):

        return Response({
            'data': 'OK',
        })
    